from rest_framework_gis import serializers as geo_serializers
from rest_framework import serializers

from django.contrib.auth.models import User, Group
from waypoints.models import Waypoint
from routes.models import Route, TrackPoint


class WaypointSerializer(geo_serializers.GeoFeatureModelSerializer):
    
    class Meta:
        model = Waypoint
        geo_field = 'the_geom'
        fields = ('fid','name','description','elevation','date','the_geom','image_path', 'route')
   
    

class TrackPointSerializer(geo_serializers.GeoFeatureModelSerializer):
    
    class Meta:
        model = TrackPoint
        geo_field = 'the_geom'
        fields = ('fid','time','ele','route')


class RouteSerializer(serializers.ModelSerializer):
    
    track_points = serializers.RelatedField(many=True)
    user = serializers.RelatedField(queryset=User.objects.all())
    group =  serializers.RelatedField(queryset=Group.objects.all())
    
    class Meta:
        model = Route
        fields = ('fid','name','description','created','image_path','user','group', 'track_points')
        
    
    
    
    
