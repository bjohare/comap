import logging, json, comap

# Get an instance of a logger
logger = logging.getLogger(__name__)

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django import forms

from forms import UploadGPXForm
from gpx_proc import GPXProc as gpx

# Geo related imports
from osgeo import ogr
import django.contrib.gis
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry

from datetime import datetime

class UploadGPXView(generic.FormView):
    template_name = 'gpx/gpx.html'
    form_class = UploadGPXForm
    success_url = '/gpx/add/'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(UploadGPXView, self).dispatch(*args, **kwargs)
    
    
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
