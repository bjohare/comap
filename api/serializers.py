import logging
from rest_framework_gis import serializers as geo_serializers
from rest_framework_gis import fields as geo_fields
from rest_framework import serializers
from datetime import datetime
from comap import settings

from django.contrib.auth.models import User, Group
from waypoints.models import Waypoint
from routes.models import Route, TrackPoint

try:
    from collections import OrderedDict
# python 2.6
except ImportError:
    from ordereddict import OrderedDict

# Get an instance of a logger
logger = logging.getLogger(__name__)



class ComapGeoFeatureModelSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    A very slightly customized GeoFeatureModelSerializer
    which only returns fields in the properties node..
    """
    
    def to_representation(self, instance):
        """
        Serialize objects -> primitives.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]

        # geo structure
        if self.Meta.id_field is not False:
            ret["id"] = ""
        ret["type"] = "Feature"
        ret["geometry"] = {}
        ret["properties"] = OrderedDict()

        for field in fields:
            field_name = field.field_name
            if field.read_only and instance is None:
                continue
            value = field.to_representation(field.get_attribute(instance))
            if self.Meta.id_field is not False and field_name == self.Meta.id_field:
                ret["id"] = value
            elif field_name == self.Meta.geo_field:
                ret["geometry"] = value
            elif not getattr(field, 'write_only', False):
                ret["properties"][field_name] = value

        if self.Meta.id_field is False:
            ret.pop(self.Meta.model._meta.pk.name)

        return ret


class SimpleRouteSerializer(serializers.Serializer):
    """ Simple serializer to provide a subset of Route fields"""
    
    fid = serializers.IntegerField()
    name = serializers.CharField()
    

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    

class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()



class WaypointSerializer(ComapGeoFeatureModelSerializer):
    """
    Serializes Waypoints. Uses SimpleRouteSerializer to return nested parent Route properties.
    """
    
    route = SimpleRouteSerializer()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Waypoint
        geo_field = 'the_geom'
        fields = ('fid','name','description','elevation','created','the_geom','image_path','image_url','route')
        read_only_fields = ('image_url')
    
    def create(self, validated_data):
        route_data = validated_data.pop('route')
        route = Route.objects.get(fid=route_data['fid'])
        return Waypoint.objects.create(route=route, **validated_data)
    
    def update(self, instance, validated_data):
        logger.debug(validated_data)
        route_data = validated_data.pop('route')
        route = Route.objects.get(fid=route_data['fid'])
        instance.route = route
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.name)
        instance.elevation = validated_data.get('elevation', instance.elevation)
        instance.image_path = validated_data.get('image_path', instance.image_path)
        instance.the_geom = validated_data.get('the_geom', instance.the_geom)
        instance.created = validated_data.get('created', instance.created)
        instance.save()
        return instance
    
    def to_internal_value(self, data):
        #TODO: might want to do more validation here but ok for now..
        route_id = data['route']
        route = Route.objects.get(fid=route_id)
        route_data = {'fid': route_id, 'name': route.name}
        created = created = datetime.now()
        name = data['name']
        description = data['description']
        elevation = data['elevation']
        image_path = data['image_path']
        the_geom = data['the_geom']
        return {'name': name, 'description': description, 'created': created,'the_geom': the_geom, 'route': route_data,
                'image_path': image_path, 'elevation': elevation}
    
    def get_image_url(self, obj):
        group = obj.route.group
        group_name = group.name.replace(" ", "_").lower()
        return '{0}/{1}/{2}/{3}/{4}/{5}'.format(settings.MEDIA_URL + str(group.id), obj.route.fid,
                                        'waypoints', obj.fid, 'images', obj.image_path)
    

class RouteSerializer(ComapGeoFeatureModelSerializer):
    
    user = UserSerializer()
    group = GroupSerializer()
    waypoints = serializers.SerializerMethodField('get_visible_waypoints')
    gpx_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Route
        geo_field = 'the_geom'
        id_field = 'fid'
        fields = ('fid','name','description','created','image_file', 'gpx_file', 'gpx_url', 'user', 'group', 'waypoints')
        read_only_fields = ('media_url')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        group_data = validated_data.pop('group')
        user = User.objects.get(id=user_data['id'])
        group = Group.objects.get(id=group_data['id'])
        return Route.objects.create(user=user, group=group, **validated_data)
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        group_data = validated_data.pop('group')
        user = User.objects.get(id=user_data['id'])
        group = Group.objects.get(id=group_data['id'])
        instance.user = user
        instance.group = group
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.name)
        instance.gpx_file = validated_data.get('gpx_file', instance.gpx_file)
        instance.image_file = validated_data.get('image_file', instance.image_file)
        instance.the_geom = validated_data.get('the_geom', instance.the_geom)
        instance.created = validated_data.get('created', instance.created)
        instance.save()
        return instance
    
    def get_visible_waypoints(self, obj):
        waypoints = Waypoint.objects.filter(route_id=obj.fid, visible=True)
        serializer = WaypointSerializer(waypoints, many=True)
        logger.debug(serializer.data)
        return serializer.data
    
    def get_gpx_url(self, obj):
        group = obj.group
        group_name = group.name.replace(" ", "_").lower()
        return '{0}/{1}/{2}/{3}'.format(settings.MEDIA_URL + str(group.id), obj.fid, 'gpx', obj.gpx_file)
    

class TrackPointSerializer(ComapGeoFeatureModelSerializer):
    
    class Meta:
        model = TrackPoint
        geo_field = 'the_geom'
        fields = ('fid','time','ele','route')
        
    

    
    
    
    
