# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.contrib.gis.db import models


class BoundaryWalkEcovillage19062014(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    symbol = models.CharField(max_length=255, blank=True)
    number = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.LineStringField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'boundary_walk_ecovillage_19_06_2014'


class BoundaryWalkEcovillageWaypoints19062014(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'boundary_walk_ecovillage_waypoints_19_06_2014'


class HeritageCycleRouteNorth12062014(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    symbol = models.CharField(max_length=255, blank=True)
    number = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.LineStringField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'heritage_cycle_route_north_12_06_2014'


class HeritageCycleRouteNorth13062014(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    symbol = models.CharField(max_length=255, blank=True)
    number = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.LineStringField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'heritage_cycle_route_north_13_06_2014'


class HeritageCycleRouteNorthWaypoints12062014(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'heritage_cycle_route_north_waypoints_12_06_2014'


class HeritageCycleRouteNorthWaypoints13062014(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'heritage_cycle_route_north_waypoints_13_06_2014'


class HeritageCycleRouteSouth23062014(models.Model):
    fid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    symbol = models.CharField(max_length=255, blank=True)
    number = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.LineStringField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'heritage_cycle_route_south_23_06_2014'


class HeritageCycleRouteSouthWaypoints23062014(models.Model):
    fid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    elevation = models.FloatField(blank=True, null=True)
    date = models.CharField(max_length=19, blank=True)
    the_geom = models.PointField(blank=True, null=True)
    image_path = models.CharField(max_length=500, blank=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'heritage_cycle_route_south_waypoints_23_06_2014'


class HeritageSouthWaypoints(models.Model):
    fid = models.IntegerField(primary_key=True)
    the_geom = models.PointField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    date = models.DateTimeField(blank=True, null=True)
    elevation = models.FloatField(blank=True, null=True)
    image_path = models.CharField(max_length=255, blank=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'heritage_south_waypoints'


class Mainstreet09062014TestRun(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=254, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=254, blank=True)
    descriptio = models.CharField(max_length=254, blank=True)
    source = models.CharField(max_length=254, blank=True)
    url = models.CharField(max_length=254, blank=True)
    url_name = models.CharField(db_column='url name', max_length=254, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'mainstreet_09_06_2014_test_run'


class VillageCycleRouteNorth(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=254, blank=True)
    symbol = models.CharField(max_length=254, blank=True)
    number = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=254, blank=True)
    descriptio = models.CharField(max_length=254, blank=True)
    source = models.CharField(max_length=254, blank=True)
    url = models.CharField(max_length=254, blank=True)
    url_name = models.CharField(db_column='url name', max_length=254, blank=True)  # Field renamed to remove unsuitable characters.
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
    url_name = models.CharField(db_column='url name', max_length=254, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.LineStringField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'village_cycle_route_south'


class WaypointImages(models.Model):
    gid = models.IntegerField(primary_key=True)
    image = models.BinaryField()
    filename = models.TextField(blank=True)
    description = models.TextField(blank=True)
    caption = models.TextField(blank=True)
    table_name = models.CharField(max_length=255, blank=True)

    class Meta:
        managed = False
        db_table = 'waypoint_images'


class WaypointsNorthInfrastructure16062014(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'waypoints_north_infrastructure_16_06_2014'


class WaypointsSouthInfrastructure16062014(models.Model):
    gid = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255, blank=True)
    elevation = models.FloatField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True)
    descriptio = models.CharField(max_length=255, blank=True)
    source = models.CharField(max_length=255, blank=True)
    url = models.CharField(max_length=255, blank=True)
    url_name = models.CharField(db_column='url name', max_length=255, blank=True)  # Field renamed to remove unsuitable characters.
    the_geom = models.PointField(blank=True, null=True)
    objects = models.GeoManager()

    class Meta:
        managed = False
        db_table = 'waypoints_south_infrastructure_16_06_2014'
