import logging, json, comap

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
from django.views import generic

from django import forms

from waypoints.models import HeritageCycleRouteSouthWaypoints23062014 as HeritageWaypoints
from waypoints.forms import EditWaypointForm, UploadGPXForm
from waypoints.gpx import GPXProc as gpx

# Geo related imports
from osgeo import ogr
import django.contrib.gis
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry

from datetime import datetime



class IndexView(generic.ListView):
    template_name = 'waypoints/index.html'
    context_object_name = 'waypoints_list'
    
    def get_queryset(self):
        return HeritageWaypoints.objects.order_by('name')


class EditView(generic.UpdateView):
    model = HeritageWaypoints
    form_class = EditWaypointForm
    context_object_name = 'waypoint'
    template_name = 'waypoints/edit.html'
    
    def get_object(self, queryset=None):
        obj = HeritageWaypoints.objects.get(fid=self.kwargs['fid'])
        return obj
    
    
    def form_valid(self, form):
        logger.debug('Edit form values: %s' % form.cleaned_data)
        fid = form.cleaned_data['fid']
        waypoint = self.get_object(fid)
        original_image_path = waypoint.image_path
        name = form.cleaned_data['name']
        description = form.cleaned_data['description']
        elevation = form.cleaned_data['elevation']
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        latitude = form.cleaned_data['latitude']
        longitude = form.cleaned_data['longitude']
        point = GEOSGeometry('POINT( ' + str(longitude) + ' ' + str(latitude) + ')') 
        waypoint.name = name
        waypoint.description = description
        waypoint.elevation = elevation
        waypoint.date = date
        waypoint.latitude = latitude
        waypoint.longitude = longitude
        waypoint.the_geom = point
        try:
            filedata = form.files['file']
            waypoint.image_path = '/' + self.__module__.split('.')[0] + '/heritage/%s' % filedata.name
            logger.debug(waypoint.image_path)
            path = comap.settings.MEDIA_ROOT + waypoint.image_path
            logger.debug('Storing image to: %s' % path)
            with open(path, 'wb+') as destination:
                for chunk in filedata.chunks():
                    destination.write(chunk)
                
        except Exception as e:
            #don't force image upload but use existing one if none provided
            logger.error(e)
            logger.debug('No image uploaded')
            waypoint.image_path = original_image_path
            pass
        
        
        # save it..
        try:
            waypoint.save()
            logger.debug('saved ok');
        except Exception as e:
            logger.error(e)    
        
        response = {}
        response["name"] = waypoint.name
        response["description"] = waypoint.description
        response["image_path"] = waypoint.image_path
        response["elevation"] = waypoint.elevation
        response["longitude"] = waypoint.longitude
        response["latitude"] = waypoint.latitude
        response["date"] = waypoint.date
        
            
        return HttpResponse(json.dumps(response), content_type="application/json", status=200)
    
    def form_invalid(self, form):
        logger.error(form.errors)
        logger.debug(type(form.errors))
        response = {}
        errors = []
        for key in form.errors:
            errors.append("".join(key))
        response["errors"] = errors
        response["status"] = 400
        response["reason"] = 'Invalid Form'
        return HttpResponse(json.dumps(response), content_type="application/json", status=400)
        

    
class UploadGPXView(generic.FormView):
    template_name = 'waypoints/gpx.html'
    form_class = UploadGPXForm
    success_url = '/waypoints/gpx/'
    
    def form_valid(self, form):
        logger.debug('upload gpx form valid...')
        logger.debug(form.cleaned_data)
        path = ''
        data_type = form.cleaned_data['data_type']
        try:
            gpxfile = form.files['gpxfile']
            gpx_path = '/' + self.__module__.split('.')[0] + '/gpx/%s' % gpxfile.name
            logger.debug(gpx_path)
            path = comap.settings.MEDIA_ROOT + gpx_path
            logger.debug('Storing gpxfile to: %s' % path)
            with open(path, 'wb+') as destination:
                for chunk in gpxfile.chunks():
                    destination.write(chunk)
        except Exception as e:
            logger.error(e)
            logger.debug('No gpx file uploaded')
        gpx(path)
        gpx.process_gpx()
        
        layer = None
        response = {}
        return HttpResponse(content='ok')
    
    def form_invalid(self, form):
        logger.error('invalid form')
        logger.error(form.errors)
        return HttpResponse(content="not ok")