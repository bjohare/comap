import logging, os, shutil, pdb
import comap
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import FileField
from rest_framework import views
from rest_framework import viewsets
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import status
from rest_framework import renderers
from rest_framework import generics
from rest_framework import filters
from rest_framework.reverse import reverse
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.parsers import FormParser,MultiPartParser
from rest_framework.response import Response

from imagekit import ImageSpec
from imagekit.processors import ResizeToFill
from cStringIO import StringIO
from PIL import Image

import django_filters

# Geo related imports
from osgeo import ogr
import django.contrib.gis
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry

from routes.models import Route, TrackPoint
from routes.gpx import GPXProc

from rest_framework.decorators import api_view, permission_classes, list_route
from waypoints.models import Waypoint, WaypointMedia
from serializers import (WaypointSerializer, RouteSerializer, PublicRouteSerializer,
                         TrackPointSerializer, WaypointMediaSerializer, UserGroupSerializer)

# Get an instance of a logger
logger = logging.getLogger(__name__)

renderer_classes = (JSONRenderer, BrowsableAPIRenderer)

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)
        

class WaypointViewSet(viewsets.ModelViewSet):
    """
    Handles api operations on Waypoints.
    Use query param 'group_id=:id' to filter by group.
    
    """
    queryset = Waypoint.objects.filter(visible=True)
    serializer_class = WaypointSerializer
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-created',)
    
    def list(self, request, pk=None, *args, **kwargs):
        route_id = self.request.QUERY_PARAMS.get('route_id', -1)
        queryset = Waypoint.objects.filter(route_id=route_id, visible=True)
        serializer = WaypointSerializer(queryset,  many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = Waypoint.objects.filter(visible=True)
        waypoint = get_object_or_404(queryset, pk=pk)
        serializer = WaypointSerializer(waypoint, context={'request': request})
        return Response(serializer.data)
    

class WaypointMediaViewSet(viewsets.ModelViewSet):
    """API endpoint for WaypointMedia operations."""
    queryset = WaypointMedia.objects.all()
    serializer_class = WaypointMediaSerializer
    
    IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif']
    AUDIO_TYPES = ['audio/mpeg', 'audio/wav', 'audio/ogg']
    VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/ogg']
    
    class ResizedImage(ImageSpec):
        processors = [ResizeToFill(500,350)]
        format = 'JPEG'
        options = {'quality': 80}
    
    def list(self, request, pk=None, *args, **kwargs):
        queryset = WaypointMedia.objects.all()
        serializer = WaypointMediaSerializer(queryset,  many=True, context={'request': request})
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        logger.debug('Adding media to waypoint')
        data = {}
        try:
            original_file = request.FILES['files[]']
            name = original_file.name.replace(' ', '_').lower()
            content_type = original_file.content_type
            size = original_file.size
            waypoint_id = request.DATA['waypoint_id']
            data = {'filename': name, 'size': size, 'waypoint_id': waypoint_id, 'content_type': content_type}
            if (content_type in self.IMAGE_TYPES):
                # resize the image
                image_generator = self.ResizedImage(source=original_file)
                rf = image_generator.generate()
                sf = SimpleUploadedFile(name=name, content=rf.getvalue(), content_type=content_type)
                data['file'] = sf
            else:
                data['file'] = original_file
        except (KeyError) as e:
            logger.error(e)
            data = {'files':[{'error': 'Server Error: {0}'.format(str(e))}]}
            return JSONResponse(data, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.object = serializer.save()
        return Response({'files': [serializer.data]}, status=status.HTTP_200_OK)
    

class RouteViewSet(viewsets.ModelViewSet):
    """
    Viewset for handling api operations on Routes
    """
    queryset = Route.objects.all().order_by('name')
    serializer_class = RouteSerializer
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-created',)
    
    class Meta:
        temp_dir = '/tmp/'
    
    def get_queryset(self,):
        user = self.request.user
        logger.debug("Username is: {0}".format(user.username))
        groups = user.groups
        return Route.objects.filter(group__in=groups.all())
    
    def list(self, request, pk=None, *args, **kwargs):
        routes = self.get_queryset()
        user = self.request.user
        if (len(routes) == 0):
            data = {
            'detail': 'No routes found'
            }
            return JSONResponse(data, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = RouteSerializer(routes,  many=True, context={'request': self.request})
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        user = self.request.user
        group_id = request.DATA['group']
        group = Group.objects.get(id=group_id)
        gpx_file = ''
        temp_gpx_file = ''
        # create a temporary gpx file to pull out the geoms
        try:
            gpxfile = request.FILES['gpxfile']
            gpx_file = gpxfile.name
            temp_gpx_file = self.Meta.temp_dir + gpxfile.name
            with open(temp_gpx_file, 'wb+') as destination:
                for chunk in gpxfile.chunks():
                    destination.write(chunk)
        except Exception as e:
            logger.error(e)
            logger.debug('No gpx file uploaded')
            
        # construct the route
        route_image_file = ''
        created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        route_name = request.DATA['name']
        route_description = request.DATA['description']
        gpx = GPXProc(temp_gpx_file)
        the_geom = gpx.get_track()
        user_data = {'id': user.id, 'username': user.username}
        group_data = {'id': group.id, 'name': group.name}
        data = {'created': created, 'the_geom': the_geom, 'description': route_description, 'name': route_name,
                     'image_file': 'none_provided', 'gpx_file': gpx_file, 'user': user_data, 'group': group_data}
        serializer = RouteSerializer(data=data, context={'request': request})
        route = None
        if (serializer.is_valid()):
            route = serializer.save()
            gpx.save_trackpoints(route.fid)
            route_paths = self.get_or_create_route_media_tree(route.fid, group.id)
            gpx_path = route_paths['gpx'] + gpx_file
            # move the gpx file from /tmp to the route media tree
            shutil.move(temp_gpx_file, gpx_path)
            # save images in there too..
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.debug(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  
        
        """
        try:
            filedata = form.files['image']
            route_image_file = '/' + self.__module__.split('.')[0] + '/heritage/%s' % filedata.name
            logger.debug(waypoint.image_file)
            path = comap.settings.MEDIA_ROOT + waypoint.image_file
            logger.debug('Storing image to: %s' % path)
            with open(path, 'wb+') as destination:
                for chunk in filedata.chunks():
                    destination.write(chunk)
                
        except Exception as e:
            #don't force image upload but use existing one if none provided
            logger.error(e)
            logger.debug('No image uploaded')
            waypoint.image_file = original_image_file
            pass
        """
    
    def update(self, request, pk=None, *args, **kwargs):
        logger.debug('Updating route with id: %s' % pk)
        partial = kwargs.pop('partial', False)
        user = self.request.user
        group_id = request.DATA['group']
        group = Group.objects.get(id=group_id)
        gpx_file = ''
        group_name = group.name.replace(" ", "_").lower()
        self.object = self.get_object()
        
        # return error if no route found..
        if self.object == None:
            return JSONResponse({'error': 'No Route found.'}, status.HTTP_404_NOT_FOUND)
        
        # check for new gpx track on form and update route. If there's no gpx to update use existing..
        gpx_file = self.object.gpx_file
        the_geom = self.object.the_geom
        image_file = self.object.image_file
        
        # create a temporary gpx file to pull out the geoms
        try:
            gpxfile = request.FILES['gpxfile']
            gpx_file = gpxfile.name
            temp_gpx_file = self.Meta.temp_dir + gpxfile.name
            with open(temp_gpx_file, 'wb+') as destination:
                for chunk in gpxfile.chunks():
                    destination.write(chunk)
            gpx = GPXProc(temp_gpx_file)
            the_geom = gpx.get_track()
            gpx.update_trackpoints(self.object.fid)
            route_paths = self.get_or_create_route_media_tree(self.object.fid, group.id)
            gpx_root = route_paths['gpx']
            # remove original gpx file
            path = gpx_root + self.object.gpx_file
            try:
                os.remove(path)
                logger.debug('Removed original gpx {0}'.format(path))
            except OSError as e:
                errstr = "Error removing gpx file: {0} : {1}".format(path, e)
                logger.warn(errstr)
            # move the gpx file from /tmp to the route media tree
            gpx_path = gpx_root + gpx_file
            shutil.move(temp_gpx_file, gpx_path)
        except Exception as e:
            logger.error(e)
            logger.debug('No gpx file uploaded')
        created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        name = request.DATA['name']
        description = request.DATA['description']
        user_data = {'id': user.id, 'username': user.username}
        group_data = {'id': group.id, 'name': group.name}
        data = {'name': name, 'description': description, 'the_geom': the_geom, 'created': created,
                'gpx_file': gpx_file, 'image_file': image_file, 'user': user_data, 'group': group_data}
        serializer = self.get_serializer(self.object, data=data, partial=partial, context={'request': request})
        if not serializer.is_valid():
            logger.debug(serializer.errors)
            return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.object = serializer.save(force_update=True)
        logger.debug('saved ok');
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def destroy(self, request, pk=None, *args, **kwargs):
        logger.debug('Deleting route with id: {0}'.format(pk))
        self.object = self.get_object()
        if self.object is not None:
            route_paths = self.get_or_create_route_media_tree(self.object.fid, self.object.group.id)
            logger.debug(route_paths)
            route_path = route_paths['route']
            if (os.path.isdir(route_path)):
                    logger.debug('Deleting route directory tree [' + route_path + ']')
                    shutil.rmtree(route_path)
        return super(RouteViewSet, self).destroy(request, *args, **kwargs)
    
    
    def get_or_create_route_media_tree(self, fid, group_id):
        user = self.request.user
        route_dir = '{0}/{1}/{2}'.format(comap.settings.MEDIA_ROOT, str(group_id), fid)
        gpx_dir = '{0}/gpx/'.format(route_dir)
        rt_image_dir = '{0}/images/'.format(route_dir)
        rt_wp_dir = '{0}/waypoints/'.format(route_dir)
        route_paths = {'route' : route_dir, 'gpx': gpx_dir, 'img': rt_image_dir, 'wp': rt_wp_dir}
        try:
            for path in route_paths.values():
                if not os.path.isdir(path):
                    try:
                        os.makedirs(path, 0770)
                        logger.debug('Created directory {0}'.format(path))
                    except OSError as e:
                        errstr = "Error creating directory: {0} : {1}".format(gpx_group_path, e)
                        logger.debug(errstr)
                        return HttpResponse(content=errstr, status=500)
            return route_paths
        except Exception as e:
            logger.error(e)


class TrackPointViewSet(viewsets.ModelViewSet):
    """
    API endpoint for listing route track points.
    Use query param 'route_id=:id' to get the points for a route.
    """
    serializer_class = TrackPointSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        route_id = self.request.QUERY_PARAMS.get('route_id', '')
        if (route_id == ''):
            return TrackPoint.objects.none()
        else:
            return TrackPoint.objects.filter(route_id=route_id)


class PublicRouteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to get a list of publicly viewable Routes.
    Used for public facing sites where authentication is not required.
    """
    serializer_class = PublicRouteSerializer
    permission_classes = (permissions.AllowAny,)
    
    def get_queryset(self):
        group_id = self.request.QUERY_PARAMS.get('group_id', -1)
        if (group_id == -1):
            return Route.objects.all()
        else:
            return Route.objects.filter(group_id=group_id)


class GetUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to get the currently logged in user.
    """
    serializer_class = UserGroupSerializer
    permission_classes = (permissions.IsAuthenticated,)
    
    def get_queryset(self):
        user = self.request.user
        logger.debug('User id: {0}'.format(user.id))
        return User.objects.filter(id=user.id)
    
