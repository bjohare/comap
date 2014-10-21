import logging
import comap
from datetime import datetime
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import mixins
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import FormParser,MultiPartParser
from rest_framework.decorators import link
from rest_framework.response import Response

# Geo related imports
from osgeo import ogr
import django.contrib.gis
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry



from waypoints.models import HeritageCycleRouteSouthWaypoints23062014 as HeritageWaypoints, GeometryColumns
from serializers import HeritageWaypointSerializer, LayersSerializer

# Get an instance of a logger
logger = logging.getLogger(__name__)

renderer_classes = (JSONRenderer)

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class WaypointViewset(viewsets.ModelViewSet):
    """
    Viewset for handling api operations on Waypoints
    """
    queryset = HeritageWaypoints.objects.all()
    serializer_class = HeritageWaypointSerializer
    parser_classes = (FormParser, MultiPartParser)
    
    def update(self, request, pk=None, *args, **kwargs):
        
        logger.debug('Saving waypoint with id: %s' % pk)
        uploaded_file = request.FILES
        partial = kwargs.pop('partial', False)
        self.object = self.get_object_or_none()
        
        # won't handle object creation here.. use create method instead if needed
        if self.object == None:
            return JSONResponse({'error': 'nothing to update'}, status.HTTP_404_NOT_FOUND)
        
        try:
            filedata = uploaded_file['file']
            image_path = '/waypoints/heritage/%s' % filedata.name
            path = comap.settings.MEDIA_ROOT + image_path
            logger.debug('Storing image to: %s' % path)
            with open(path, 'wb+') as destination:
                for chunk in filedata.chunks():
                    destination.write(chunk)
            self.object.image_path = image_path
        except Exception as e:
            #don't force image upload but use existing one if none provided
            logger.error(e)
            logger.debug('No image uploaded')
            pass
        
        serializer = self.get_serializer(self.object, data=request.DATA,
                                     files=request.FILES, partial=partial)
        
        self.object.date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        
        if not serializer.is_valid():
            return JSONResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        self.object = serializer.save(force_update=True)
        self.post_save(self.object, created=False)
        logger.debug('saved ok');
        return JSONResponse(serializer.data, status=status.HTTP_200_OK)
        
        
class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """A custom viewset providing just list behaviour"""
    pass


class LayersViewset(ListViewSet):
    queryset = GeometryColumns.objects.all()
    serializer_class = LayersSerializer
    
    
