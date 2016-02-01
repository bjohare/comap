from __future__ import unicode_literals

import logging
import shutil
import os

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver

from routes.models import Route

# Get an instance of a logger
logger = logging.getLogger(__name__)

# construct the upload path for WaypointMedia objects


def get_upload_path(instance, filename):
    waypoint = instance.waypoint
    route = waypoint.route
    group = route.group_id
    content_type = instance.content_type.split('/')[0]
    path = '{0}/{1}/waypoints/{2}/{3}/{4}'.format(
        group, route.fid, waypoint.fid, content_type, instance.filename)
    logger.debug('Saving file to {0}'.format(path))
    return path


class Waypoint(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=65000, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(null=True)
    the_geom = models.PointField(blank=True, null=True, srid=4326)
    route = models.ForeignKey('routes.Route', related_name='waypoints')
    visible = models.BooleanField(default=False)
    objects = models.GeoManager()

    def __str__(self):
        return 'Name: {name}, Route: {route}, Visible: {visible}'.format(name=self.name, route=self.route.name, visible=self.visible)

    class Meta:
        managed = True
        db_table = 'waypoints'


class WaypointMedia(models.Model):
    fid = models.AutoField(primary_key=True)
    content_type = models.CharField(max_length=100, blank=False)
    filename = models.CharField(max_length=100, blank=False)
    size = models.IntegerField()
    file = models.FileField(max_length=255, upload_to=get_upload_path)
    waypoint = models.ForeignKey(Waypoint, related_name='waypoint_media')
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'waypoint_media'

    def __str__(self):
        return 'WaypointMedia[fid: {}, filename: {}, content_type: {}, created: {}, waypoint: {}]'.format(self.fid, self.filename, self.content_type, self.created, self.waypoint_id)


# force deletion of file when model instance is deleted.
@receiver(post_delete, sender=WaypointMedia)
def delete_waypointmedia(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    logger.debug('Deleting WaypointMedia file: {0}'.format(instance.file.name))
    instance.file.delete(False)


@receiver(post_delete, sender=Waypoint)
def delete_waypoint_dir(sender, instance, **kwargs):
    # force deletion of the waypoint directory when model instance is deleted.
    route = instance.route
    group = route.group
    path = '{0}/{1}/{2}/waypoints/{3}'.format(
        settings.MEDIA_ROOT, group.id, route.fid, instance.fid)
    if (os.path.isdir(path)):
        logger.debug('Deleting Waypoint directory: {0}'.format(path))
        shutil.rmtree(path)
