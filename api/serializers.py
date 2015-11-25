import logging, pdb
from rest_framework_gis import serializers as geo_serializers
from rest_framework_gis import fields as geo_fields
from rest_framework import serializers
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User, Group
from waypoints.models import Waypoint, WaypointMedia
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

class GroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    
    
class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    

class UserGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    groups = GroupSerializer(many=True)
    

class SimpleRouteSerializer(serializers.Serializer):
    """ Simple serializer to provide a subset of Route fields"""
    
    fid = serializers.IntegerField()
    name = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(
        view_name="api:tracks-detail",
    )
    group = GroupSerializer()
    

class SimpleWaypointSerializer(serializers.Serializer):
    """ Simple serializer to provide a subset of Waypoint fields"""
    
    fid = serializers.IntegerField()
    name = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(
        view_name="api:waypoints-detail",
    )
    

class WaypointSerializer(ComapGeoFeatureModelSerializer):
    """
    Serializes Waypoints. Uses SimpleRouteSerializer to return nested parent Route properties.
    """
    
    route = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    
    class Meta:
        model = Waypoint
        geo_field = 'the_geom'
        fields = ('fid','name','description','elevation','created','the_geom','media','route')
    
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
        the_geom = data['the_geom']
        return {'name': name, 'description': description, 'created': created,'the_geom': the_geom, 'route': route_data, 'elevation': elevation}
    
    def get_media(self, obj):
        media = WaypointMedia.objects.filter(waypoint_id=obj.fid)
        serializer = WaypointMediaSerializer(media, many=True, context=self.context)
        return {'files': serializer.data}
    
    def get_route(self, obj):
        route = obj.route
        serializer = SimpleRouteSerializer(route, context=self.context)
        return serializer.data
    

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
        waypoints = Waypoint.objects.filter(route_id=obj.fid)
        serializer = WaypointSerializer(waypoints, many=True, context=self.context)
        logger.debug(serializer.data)
        return serializer.data
    
    def get_gpx_url(self, obj):
        group = obj.group
        group_name = group.name.replace(" ", "_").lower()
        return '{0}/{1}/{2}/{3}'.format(settings.MEDIA_URL + str(group.id), obj.fid, 'gpx', obj.gpx_file)
    
    
class PublicRouteSerializer(ComapGeoFeatureModelSerializer):
    
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

    
    def get_visible_waypoints(self, obj):
        waypoints = Waypoint.objects.filter(route_id=obj.fid, visible=True)
        serializer = WaypointSerializer(waypoints, many=True, context=self.context)
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
        
    
class WaypointMediaSerializer(serializers.ModelSerializer):
    
    waypoint = SimpleWaypointSerializer()
    media_url = serializers.SerializerMethodField()
    url = serializers.HyperlinkedIdentityField(
        view_name="api:waypointmedia-detail",
    )
    
    class Meta:
        model = WaypointMedia
        fields = ('fid','filename','content_type','size','created','updated','media_url','url','waypoint')
    
    def create(self, validated_data):
        waypoint_data = validated_data.pop('waypoint_data')
        waypoint_id = waypoint_data['fid']
        waypoint = Waypoint.objects.get(fid=waypoint_id)
        return WaypointMedia.objects.create(waypoint=waypoint, **validated_data)
    
    def to_internal_value(self, data):
        waypoint_id = data['waypoint_id']
        logger.debug(waypoint_id)
        waypoint = Waypoint.objects.get(fid=waypoint_id)
        waypoint_data = {'fid': waypoint_id, 'name': waypoint.name}
        filename = data['filename']
        size = data['size']
        file = data['file']
        content_type = data['content_type']
        return {'filename': filename, 'size': size, 'waypoint_data': waypoint_data, 'content_type': content_type, 'file': file}
    
    def get_media_url(self, obj):
        return obj.file.url
    
    
