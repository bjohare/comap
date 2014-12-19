from __future__ import unicode_literals

from django.contrib.gis.db import models

class Waypoints(models.Model):
    fid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    date = models.CharField(max_length=19, blank=True)
    the_geom = models.PointField(blank=True, null=True, srid=4326)
    image_path = models.CharField(max_length=500, blank=True)
    objects = models.GeoManager()
    owner = models.ForeignKey('auth.User', related_name='waypoints')
    def __str__(self):
        return self.name
    class Meta:
        managed = True
        db_table = 'waypoints'


""" Leave these here for now as examples 
class VillageCycleRouteNorth(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=254, blank=True)
    symbol = models.CharField(max_length=254, blank=True)
    number = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=254, blank=True)
    descriptio = models.CharField(max_length=254, blank=True)
    source = models.CharField(max_length=254, blank=True)
    url = models.CharField(max_length=254, blank=True)
    url_name = models.CharField(db_column='url name', max_length=254, blank=True) # Field renamed to remove unsuitable characters.
    the_geom = models.LineStringField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'village_cycle_route_north'


class VillageCycleRouteSouth(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=254, blank=True)
    symbol = models.CharField(max_length=254, blank=True)
    number = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=254, blank=True)
    descriptio = models.CharField(max_length=254, blank=True)
    source = models.CharField(max_length=254, blank=True)
    url = models.CharField(max_length=254, blank=True)
    url_name = models.CharField(db_column='url name', max_length=254, blank=True) # Field renamed to remove unsuitable characters.
    the_geom = models.LineStringField(blank=True, null=True)
    objects = models.GeoManager()
    class Meta:
        managed = False
        db_table = 'village_cycle_route_south'
"""

"""
class GeometryColumns(models.Model):
    table_name = models.CharField(max_length=256, primary_key=True, db_column='f_table_name')
    srid = models.IntegerField()
    geom_type = models.CharField(max_length=30, db_column='type')
    
    class Meta:
        managed = False
        ordering = ['table_name']
        db_table = 'geometry_columns'
"""

    
    


