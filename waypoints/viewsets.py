from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import link
from rest_framework.response import Response
from rest_framework import mixins
from waypoints.models import HeritageCycleRouteSouthWaypoints23062014 as HeritageWaypoints, GeometryColumns
from serializers import HeritageWaypointSerializer, LayersSerializer

class WaypointViewset(viewsets.ModelViewSet):
    queryset = HeritageWaypoints.objects.all()
    serializer_class = HeritageWaypointSerializer


class ListViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """A custom viewset providing just list behaviour"""
    pass


class LayersViewset(ListViewSet):
    queryset = GeometryColumns.objects.all()
    serializer_class = LayersSerializer
    
    
