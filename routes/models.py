from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group

class Route(models.Model):
    """Model for a Route"""
    fid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='route_user')
    group = models.ForeignKey(Group, related_name='route_groups')
    created = models.DateTimeField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=65000)
    image_file = models.CharField(max_length=100)   
    gpx_file = models.CharField(max_length=100)
    the_geom = models.MultiLineStringField()
    objects = models.GeoManager()
    class Meta:
        managed = True
        db_table = 'routes'
    def __str__(self):
        return 'Route[fid: {}, name: {}, description: {}, created: {}, user: {}, group: {}]'.format(self.fid, self.name, self.description, self.created, self.user_id, self.group_id)

class TrackPoint(models.Model):
    """GPX track_points for a route"""
    fid = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, related_name='track_points')
    ele = models.DecimalField(max_digits=7, decimal_places=2, null=True)   
    time = models.DateTimeField(null=True)
    the_geom = models.PointField()
    objects = models.GeoManager()
    class Meta:
        managed = True
        db_table = 'track_points'
    def __str__(self):
        return 'TrackPoint[fid: {}, elevation: {}, geom: {}, time: {}, route: {}]'.format(self.fid, self.ele, self.the_geom, self.time, self.route_id)
    
    
