from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group

class Route(models.Model):
    fid = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, related_name='route')
    user = models.ForeignKey(User, related_name='route')
    created = models.DateTimeField()
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=65000)
    image_path = models.CharField(max_length=500)
    class Meta:
        managed = True
        db_table = 'routes'
    def __str__(self):
        return 'Route[fid: {}, name: {}, description: {}, time: {}, user: {}, group: {}]'.format(self.fid, self.name, self.description, self.time, self.user_id, self.group_id)


class TrackPoint(models.Model):
    fid = models.AutoField(primary_key=True)
    route = models.ForeignKey(Route, related_name='track_points')
    user = models.ForeignKey(User, related_name='track_points')
    group = models.ForeignKey(Group, related_name='track_points')
    ele = models.DecimalField(max_digits=7, decimal_places=2)
    time = models.DateTimeField()
    the_geom = models.PointField()
    objects = models.GeoManager()
    class Meta:
        managed = True
        db_table = 'track_points'
    def __str__(self):
        return 'TrackPoint[fid: {}, elevation: {}, geom: {}, time: {}, user: {}, group: {}, route: {}]'.format(self.fid, self.ele, self.the_geom, self.time, self.user_id, self.group_id, self.route_id)
    
    

