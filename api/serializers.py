from rest_framework_gis import serializers as geo_serializers
from rest_framework import serializers

from django.contrib.auth.models import User
from waypoints.models import Waypoints
from gpx.models import Route

class WaypointSerializer(geo_serializers.GeoFeatureModelSerializer):
    
    class Meta:
        model = Waypoints
        geo_field = 'the_geom'
        fields = ('fid','name','description','elevation','date','the_geom','image_path', 'owner')
    
    owner = serializers.Field(source='owner.username')


class RouteSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Route
        fields = ('fid','name','description','created','image_path','user','group')
