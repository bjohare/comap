from __future__ import unicode_literals

from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from routes.models import Route

class Waypoint(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    date = models.CharField(max_length=19, blank=True)
    the_geom = models.PointField(blank=True, null=True, srid=4326)
    image_path = models.CharField(max_length=500, blank=True)
    route = models.ForeignKey('routes.Route', related_name='wp_routes')
    objects = models.GeoManager()
    
    def __str__(self):
        return 'Waypoint[fid: {}, name: {}, description: {}, date: {}, route: {}]'.format(self.fid, self.name, self.description, self.date, self.route_id)
    
    class Meta:
        managed = True
        db_table = 'waypoints'
    
    


