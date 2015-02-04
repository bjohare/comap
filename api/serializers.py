from rest_framework_gis import serializers as geo_serializers
from rest_framework_gis import fields as geo_fields
from rest_framework import serializers

from django.contrib.auth.models import User, Group
from waypoints.models import Waypoint
from routes.models import Route, TrackPoint


class WaypointSerializer(geo_serializers.GeoFeatureModelSerializer):
    
    class Meta:
        model = Waypoint
        geo_field = 'the_geom'
        fields = ('fid','name','description','elevation','created','the_geom','image_path', 'route')
        
    def transform_route(self, object, value):
        if (object == None):
            return None
        else:
            return object.route.name


class RouteSerializer(geo_serializers.GeoFeatureModelSerializer):
    
    waypoints = WaypointSerializer(many=True)
    
    class Meta:
        model = Route
        geo_field = 'the_geom'
        read_only_fields = ['user','group']
        fields = ('fid','name','description','created','image_file', 'gpx_file', 'user', 'group', 'waypoints')
        
    def transform_user(self, object, value):
        return object.user.username
    
    def transform_group(self, object, value):
        return object.group.name





class TrackPointSerializer(geo_serializers.GeoFeatureModelSerializer):
    
    class Meta:
        model = TrackPoint
        geo_field = 'the_geom'
        fields = ('fid','time','ele','route')
        
    

    
    
    
    
