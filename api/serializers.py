from rest_framework_gis import serializers
from django.contrib.auth.models import User
from waypoints.models import Waypoints as HeritageWaypoints, GeometryColumns

class HeritageWaypointSerializer(serializers.GeoFeatureModelSerializer):
    
    class Meta:
        model = HeritageWaypoints
        geo_field = 'the_geom'
        fields = ('fid','name','description','elevation','date','the_geom','image_path')


class LayersSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GeometryColumns
        fields = ('table_name','srid','geom_type')
