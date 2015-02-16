import logging, os, shutil
import comap
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
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

import django_filters

# Geo related imports
from osgeo import ogr
import django.contrib.gis
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry

from routes.models import Route, TrackPoint
from routes.gpx import GPXProc

from rest_framework.decorators import api_view
from waypoints.models import Waypoint
from serializers import WaypointSerializer, RouteSerializer, TrackPointSerializer

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
    Viewset for handling api operations on Waypoints
    """
    queryset = Waypoint.objects.filter(visible=True)
    serializer_class = WaypointSerializer
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-created',)
    
    def list(self, request, pk=None, *args, **kwargs):
        route_id = self.request.QUERY_PARAMS.get('route_id', -1)
        queryset = Waypoint.objects.filter(route_id=route_id, visible=True)
        serializer = WaypointSerializer(queryset,  many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = Waypoint.objects.filter(visible=True)
        waypoint = get_object_or_404(queryset, pk=pk)
        serializer = WaypointSerializer(waypoint)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        logger.debug('Creating a new waypoint')
        uploaded_file = request.FILES
        image_path = 'none_provided'
        route_id = request.DATA['route']
        filedata = None
        try:
            filedata = uploaded_file['file']
            image_path = filedata.name
        except (KeyError) as e:
            logger.error(e)
            logger.debug('No image uploaded')
        request.DATA['image_path'] = image_path
        serializer = self.get_serializer(data=request.DATA)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.object = serializer.save()
        if filedata is not None:
            self.handle_file_uploads(filedata)
        logger.debug('Waypoint created ok');
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, pk=None, *args, **kwargs):
        logger.debug('Updating waypoint with id: %s' % pk)
        uploaded_file = request.FILES
        partial = kwargs.pop('partial', False)
        self.object = self.get_object()
        if self.object == None:
            return JSONResponse({'error': 'no waypoint to update'}, status.HTTP_404_NOT_FOUND)
        image_path = self.object.image_path # default to existing
        path = ''
        try:
            filedata = uploaded_file['file']
            image_path = filedata.name
            waypoint_paths = self.get_or_create_waypoint_media_tree()
            # remove the existing image and save the new one..
            try:
                path = waypoint_paths['image'] + self.object.image_path
                os.remove(path)
                logger.debug('Removed original image {0}'.format(path))
                # save the new one..
                path = waypoint_paths['image'] + image_path
                with open(path, 'wb+') as destination:
                    for chunk in filedata.chunks():
                        destination.write(chunk)
            except OSError as e:
                errstr = "Error removing image: {0} : {1}".format(path, e)
                logger.warn(errstr)
        except KeyError as e:
            #don't force image upload but use existing one if none provided
            logger.error(e)
            logger.debug('No image uploaded')
        request.DATA['image_path'] = image_path
        serializer = self.get_serializer(self.object, data=request.DATA, partial=partial)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.object = serializer.save(force_update=True)
        logger.debug('Waypoint updated ok');
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        logger.debug('Deleting waypoint with id: {0}'.format(pk))
        self.object = self.get_object()
        waypoint_paths = self.get_or_create_waypoint_media_tree()
        path = waypoint_paths['waypoint']
        if self.object is not None:
            if (os.path.isdir(path)):
                logger.debug('Deleting waypoint directory tree [' + path + ']')
                shutil.rmtree(path)
        return super(WaypointViewSet, self).destroy(request, *args, **kwargs)
        
    def handle_file_uploads(self, filedata, *args, **kwargs):
        waypoint_paths = self.get_or_create_waypoint_media_tree()
        image_path = waypoint_paths['image'] + filedata.name
        # do image processing here.. then save it..
        try:
            with open(image_path, 'wb+') as destination:
                for chunk in filedata.chunks():
                    destination.write(chunk)
        except OSError as e:
            pass
    
    def get_or_create_waypoint_media_tree(self, *args, **kwargs):
        user = self.request.user
        group = user.groups.get()
        group_name = group.name.replace(" ", "_").lower()
        fid = self.object.fid
        route_id = self.object.route.fid
        waypoint_dir = '{0}/{1}/{2}/waypoints/{3}'.format(comap.settings.MEDIA_ROOT, group_name, route_id, fid)
        wp_image_dir = '{0}/images/'.format(waypoint_dir)
        wp_audio_dir = '{0}/audio/'.format(waypoint_dir)
        wp_video_dir = '{0}/video/'.format(waypoint_dir)
        waypoint_paths = {'waypoint' : waypoint_dir, 'image': wp_image_dir,
                          'audio': wp_audio_dir, 'video': wp_video_dir}
        logger.debug(waypoint_paths)
        try:
            for path in waypoint_paths.values():
                if not os.path.isdir(path):
                    try:
                        os.makedirs(path, 0770)
                        logger.debug('Created directory {0}'.format(path))
                    except OSError as e:
                        errstr = "Error creating directory: {0} : {1}".format(gpx_group_path, e)
                        logger.debug(errstr)
                        return HttpResponse(content=errstr, status=500)
            return waypoint_paths
        except Exception as e:
            logger.error(e)


class RouteViewSet(viewsets.ModelViewSet):
    """
    Viewset for handling api operations on Routes
    """
    queryset = Route.objects.all().order_by('name')
    serializer_class = RouteSerializer
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (filters.OrderingFilter,)
    ordering = ('-created',)
    
    class Meta:
        temp_dir = '/tmp/'
    
    def get_queryset(self,):
        user = self.request.user
        logger.debug("Username is: {0}".format(user.username))
        group = user.groups.get()
        logger.debug("Listing Routes for group {0}".format(group.name))
        return Route.objects.filter(group_id=group.id)
    
    def list(self, request, pk=None, *args, **kwargs):
        routes = self.get_queryset()
        user = self.request.user
        group = user.groups.get()
        if (len(routes) == 0):
            data = {
            'detail': 'No routes found for {0}'.format(group.name),
            }
            return JSONResponse(data, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = RouteSerializer(routes,  many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        user = self.request.user
        group = user.groups.get()
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
        serializer = RouteSerializer(data=data)
        route = None
        if (serializer.is_valid()):
            route = serializer.save()
            gpx.save_trackpoints(route.fid)
            route_paths = self.get_or_create_route_media_tree(route.fid)
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
        group = user.groups.get()
        gpx_file = ''
        group_name = group.name.replace(" ", "_").lower()
        self.object = self.get_object()
        
        # return error if no route found..
        if self.object == None:
            return JSONResponse({'error': 'no route to update'}, status.HTTP_404_NOT_FOUND)
        
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
            route_paths = self.get_or_create_route_media_tree(self.object.fid)
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
        serializer = self.get_serializer(self.object, data=data, partial=partial)
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
            route_paths = self.get_or_create_route_media_tree(self.object.fid)
            logger.debug(route_paths)
            route_path = route_paths['route']
            if (os.path.isdir(route_path)):
                    logger.debug('Deleting route directory tree [' + route_path + ']')
                    shutil.rmtree(route_path)
        return super(RouteViewSet, self).destroy(request, *args, **kwargs)
    
    
    def get_or_create_route_media_tree(self, fid):
        user = self.request.user
        group = user.groups.get()
        group_name = group.name.replace(" ", "_").lower()
        route_dir = '{0}/{1}/{2}'.format(comap.settings.MEDIA_ROOT, group_name, fid)
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
    
    serializer_class = TrackPointSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        route_id = self.request.QUERY_PARAMS.get('route_id', '')
        if (route_id == ''):
            return TrackPoint.objects.none()
        else:
            return TrackPoint.objects.filter(route_id=route_id)


"""
@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'waypoints': reverse('waypoints-list', request=request, format=format),
        'points': reverse('points-list', request=request, format=format),
        #'tracks': reverse('tracks-list', request=request, format=format),
})
"""
