import logging
import json
import os
import pwd
from datetime import datetime

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.conf import settings
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

# Get an instance of a logger
logger = logging.getLogger(__name__)


class RouteListView(generic.ListView):

    """
    View to render list of routes. Filtered by group.
    """
    template_name = 'routes/list.html'
    context_object_name = 'routes_list'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RouteListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        logger.debug("Username is: {0}".format(user.username))
        group = user.groups.get()
        logger.debug("Listing Routes for group {0}".format(group.name))
        return Route.objects.filter(group_id=group.id)

    def get_context_data(self, *args, **kwargs):
        context = super(RouteListView, self).get_context_data(**kwargs)
        user = self.request.user
        logger.debug("Username is: {0}".format(user.username))
        group = user.groups.get()
        logger.debug("Listing Routes for group {0}".format(group.name))
        context['user'] = user
        context['group'] = group
        return context


class RouteAddView(generic.FormView):
    template_name = 'routes/create.html'
    form_class = RouteAddForm
    success_url = '/route/add/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RouteAddView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        logger.debug('Route creation form is valid...')
        gpx_path = ''
        user = self.request.user
        group = user.groups.get()
        group_name = group.name.replace(" ", "_").lower()
        logger.debug(
            "User is: {0}, Group is: {1}".format(user.username, group_name))
        try:
            gpxfile = form.files['gpxfile']
            gpx_group_path = settings.GPX_ROOT + \
                self.__module__.split('.')[0] + '/' + group_name
            gpx_path = gpx_group_path + '/%s' % gpxfile.name
            logger.debug("Checking for path [{0}]..".format(gpx_group_path))
            if not os.path.isdir(gpx_group_path):
                try:
                    logger.debug(
                        "No root gpx directory for group {0}.. creating..".format(group_name))
                    os.makedirs(gpx_group_path, 0770)
                    #uid, gid =  pwd.getpwnam('ubuntu').pw_uid, pwd.getpwnam('www-data').pw_uid
                    #os.chown(gpx_group_path, uid, gid)
                except OSError as e:
                    errstr = "Error creating root gpx directory: {0} : {2}".format(
                        gpx_group_path, e)
                    logger.debug(errstr)
                    return HttpResponse(content=errstr, status=400)
            logger.debug('Storing gpxfile to: %s' % gpx_path)
            with open(gpx_path, 'wb+') as destination:
                for chunk in gpxfile.chunks():
                    destination.write(chunk)
        except Exception as e:
            logger.error(e)
            logger.debug('No gpx file uploaded')
        # create route now
        route_name = form.cleaned_data['name']
        route_description = form.cleaned_data['description']
        created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        route_image_path = ''
        """
        try:
            filedata = form.files['image']
            route_image_path = '/' + self.__module__.split('.')[0] + '/heritage/%s' % filedata.name
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
        """
        # construct the route here but dont save until we extract the track
        route = Route(name=route_name, description=route_description,
                      created=created, image_path='none_provided', user_id=user.id, group_id=group.id)
        gpx = GPXProc(gpx_path, route)
        gpx.process_gpx()

        layer = None
        response = {}
        return HttpResponse(content='ok')

    def form_invalid(self, form):
        logger.error('invalid form')
        logger.error(form.errors)
        return HttpResponse(content="not ok")
