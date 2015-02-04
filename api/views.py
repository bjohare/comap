import logging, os
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
from rest_framework.decorators import link
from rest_framework.response import Response

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
    queryset = Waypoint.objects.all()
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
    
    
    """
    def create(self, request, *args, **kwargs):
        logger.debug('In waypoint create method')
        serializer = self.get_serializer(self.object, data=request.DATA,
                                     files=request.FILES, partial=partial)
        return JSONResponse({'error': 'working on it'}, status.HTTP_200_OK)
    """
    
    def update(self, request, pk=None, *args, **kwargs):
        logger.debug('Saving waypoint with id: %s' % pk)
        uploaded_file = request.FILES
        partial = kwargs.pop('partial', False)
        self.object = self.get_object_or_none()
        
        # won't handle object creation here.. use create method instead if needed
        if self.object == None:
            return JSONResponse({'error': 'no waypoint to update'}, status.HTTP_404_NOT_FOUND)
        
        try:
            filedata = uploaded_file['file']
            image_file = '/waypoints/heritage/%s' % filedata.name
            path = comap.settings.MEDIA_ROOT + image_file
            logger.debug('Storing image to: %s' % path)
            with open(path, 'wb+') as destination:
                for chunk in filedata.chunks():
                    destination.write(chunk)
            self.object.image_file = image_file
        except Exception as e:
            #don't force image upload but use existing one if none provided
            logger.error(e)
            logger.debug('No image uploaded')
        
        
        serializer = self.get_serializer(self.object, data=request.DATA,
                                     files=request.FILES, partial=partial)
        
        self.object.created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.object = serializer.save(users=request.user, groups=request.user.groups.get(), force_update=True)
        self.post_save(self.object, created=False)
        logger.debug('saved ok');
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def destroy(self, request, pk=None, *args, **kwargs):
        logger.debug('Deleting waypoint with id: {0}'.format(pk))
        self.object = self.get_object_or_none()
        logger.debug(self.object.name)
        """
        if (os.path.isfile(existing_path)):
                logger.debug('Deleting [' + existing_path + ']')
                os.remove(existing_path)
        """
        return super(WaypointViewSet, self).destroy(request, *args, **kwargs)
        
        

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
    
    def get_queryset(self,):
        user = self.request.user
        logger.debug("Username is: {0}".format(user.username))
        group = user.groups.get()
        logger.debug("Listing Routes for group {0}".format(group.name))
        return Route.objects.filter(group_id=group.id)
    
    
    def create(self, request, *args, **kwargs):
        user = self.request.user
        group = user.groups.get()
        gpx_file = ''
        group_name = group.name.replace(" ", "_").lower()
        logger.debug("User is: {0}, Group is: {1}".format(user.username, group_name))
        
        try:
            gpxfile = request.FILES['gpxfile']
            gpx_group_path = comap.settings.GPX_ROOT + group_name
            gpx_file = gpx_group_path + '/%s' % gpxfile.name
            logger.debug("Checking for path [{0}]..".format(gpx_group_path))
            if not os.path.isdir(gpx_group_path):
                try:
                    logger.debug("No root gpx directory for group {0}.. creating..".format(group_name))
                    os.makedirs(gpx_group_path, 0770)
                    #uid, gid =  pwd.getpwnam('ubuntu').pw_uid, pwd.getpwnam('www-data').pw_uid
                    #os.chown(gpx_group_path, uid, gid)
                except OSError as e:
                    errstr = "Error creating root gpx directory: {0} : {2}".format(gpx_group_path, e)
                    logger.debug(errstr)
                    return HttpResponse(content=errstr, status=400)
            logger.debug('Storing gpxfile to: %s' % gpx_file)
            with open(gpx_file, 'wb+') as destination:
                for chunk in gpxfile.chunks():
                    destination.write(chunk)
        except Exception as e:
            logger.error(e)
            logger.debug('No gpx file uploaded')
            
        # construct the route here but dont save until we extract the track
        route_image_file = ''
        created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        route_name = request.DATA['name']
        route_description = request.DATA['description']
        gpx = GPXProc(gpx_file)
        the_geom = gpx.get_track()
        valid_data = {'created': created, 'the_geom': the_geom, 'description': route_description, 'name': route_name,
                      'image_file': 'none_provided', 'gpx_file': gpx_file}
        logger.debug(valid_data)
        """
        route = Route(name=route_name, description=route_description,
                        created=created, image_file='none_provided', user_id=user.id,
                        group_id=group.id, gpx_file='a path', the_geom=the_geom)
        """
        serializer = RouteSerializer(data=valid_data)
        route = None
        if (serializer.is_valid()):
            serializer.object.user = user;
            serializer.object.group = group;
            route = serializer.save()
            gpx.save_trackpoints(route.fid)
            logger.debug(serializer.data)
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
        self.object = self.get_object_or_none()
        
        # return error if no route found..
        if self.object == None:
            return JSONResponse({'error': 'no route to update'}, status.HTTP_404_NOT_FOUND)
        
        # check for new gpx track on form and update route. If there's no gpx to update use existing..
        gpx_file = self.object.gpx_file
        the_geom = self.object.the_geom
        image_file = self.object.image_file
        try:
            gpxfile = request.FILES['gpxfile']
            gpx_group_path = comap.settings.GPX_ROOT + group_name
            gpx_file = gpx_group_path + '/%s' % gpxfile.name
            existing_path = self.object.gpx_file
            if (os.path.isfile(existing_path)):
                logger.debug('Found existing gpx file for this route. Deleting [' + existing_path + ']')
                os.remove(existing_path)
            logger.debug("Checking for path [{0}]..".format(gpx_group_path))
            if not os.path.isdir(gpx_group_path):
                try:
                    logger.debug("No root gpx directory for group {0}.. creating..".format(group_name))
                    os.makedirs(gpx_group_path, 0770)
                except OSError as e:
                    errstr = "Error creating root gpx directory: {0} : {2}".format(gpx_group_path, e)
                    logger.debug(errstr)
                    return HttpResponse(content=errstr, status=400)
            logger.debug('Storing gpxfile to: %s' % gpx_file)
            with open(gpx_file, 'wb+') as destination:
                for chunk in gpxfile.chunks():
                    destination.write(chunk)
            # pull out the new track and trackpoints
            gpx = GPXProc(gpx_file)
            the_geom = gpx.get_track()
            gpx.update_trackpoints(self.object.fid)
        except Exception as e:
            logger.error(e)
            logger.debug('No gpx file uploaded')
        
        created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        name = request.DATA['name']
        description = request.DATA['description']
        data = {'name': name, 'description': description, 'the_geom': the_geom, 'created': created,
                'gpx_file': gpx_file, 'image_file': image_file}
        serializer = self.get_serializer(self.object, data=data,
                                    files=request.FILES, partial=partial)
        
        if not serializer.is_valid():
            logger.debug(serializer.errors)
            return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.object = serializer.save(force_update=True)
        self.post_save(self.object, created=False)
        logger.debug('saved ok');
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def destroy(self, request, pk=None, *args, **kwargs):
        logger.debug('Deleting route with id: {0}'.format(pk))
        self.object = self.get_object_or_none()
        existing_path = self.object.gpx_file
        if (os.path.isfile(existing_path)):
                logger.debug('Deleting [' + existing_path + ']')
                os.remove(existing_path)
        return super(RouteViewSet, self).destroy(request, *args, **kwargs)
        

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
