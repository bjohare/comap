import logging, json, comap, os, pwd

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

from models import Route
from forms import RouteAddForm
from gpx import GPXProc

# Geo related imports
from osgeo import ogr
import django.contrib.gis
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry

from datetime import datetime

class RouteAddView(generic.FormView):
    template_name = 'routes/route.html'
    form_class = RouteAddForm
    success_url = '/route/add/'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RouteAddView, self).dispatch(*args, **kwargs)
    
    
    def form_valid(self, form):
        logger.debug('Route creation form is valid...')
        logger.debug('User is %s' % self.request.user)
        logger.debug(form.cleaned_data)
        gpx_path = ''
        user = self.request.user
        group = user.groups.get() 
        group_name = group.name.replace(" ", "_").lower()
        logger.debug('Group is: %s', group_name)
        try:
            gpxfile = form.files['gpxfile']
            gpx_group_path = comap.settings.GPX_ROOT + self.__module__.split('.')[0] + '/' + group_name
            gpx_path = gpx_group_path + '/%s' % gpxfile.name
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
            logger.debug('Storing gpxfile to: %s' % gpx_path)
            with open(gpx_path, 'wb+') as destination:
                for chunk in gpxfile.chunks():
                    destination.write(chunk)
        except Exception as e:
            logger.error(e)
            logger.debug('No gpx file uploaded')
        # create route here
        route = Route.objects.create(name='Mountain Walk', description='A Mountain Walk',
                                     created='2012-05-20 14:10:31', image_path='/image.jpg', user_id=user.id, group_id=group.id)
        gpx = GPXProc(gpx_path, route)
        gpx.process_gpx()
        
        layer = None
        response = {}
        return HttpResponse(content='ok')
    
    def form_invalid(self, form):
        logger.error('invalid form')
        logger.error(form.errors)
        return HttpResponse(content="not ok")
