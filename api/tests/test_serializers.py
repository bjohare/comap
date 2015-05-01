import logging, sys, pdb, json

from rest_framework.reverse import reverse
from django.test import TestCase
from rest_framework.test import (APIRequestFactory, force_authenticate, APITestCase)
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpRequest

from routes.models import Route
from waypoints.models import Waypoint, WaypointMedia

from api.views import (WaypointMediaViewSet, WaypointViewSet)
from api.serializers import WaypointSerializer

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class WaypointSerializerTestCase(TestCase):
    
    def setUp(self):
        self.group = Group.objects.create(name='Knockatallon Ramblers')
        self.user = User.objects.create_user(
            username='frank', email='frank@frank.com', password='frank'
        )
        self.user.groups = [self.group]
        linestring = GEOSGeometry('MULTILINESTRING((-7.10411262698471 54.3239101488143,-7.10412142798305 54.3239141721278,-7.10410986095667 54.3239162676036,-7.10410818457604 54.3238997552544,-7.1040909178555 54.3239010125399))')
        Route.objects.create(name='TestRoute', description='Test Route Description', the_geom=linestring, user_id=1, group_id=1, created='2012-05-20 14:10:31', image_file='/image.jpg')
        point = GEOSGeometry('POINT (-7.102992720901966 54.326739795506001)')
        Waypoint.objects.create(name='Ballycapple Castle', description='Some descriptive text',
                                elevation=223.45, created='2012-05-20 14:10:31', the_geom = point, route_id=1)
        WaypointMedia.objects.create(filename='TestFile',waypoint_id=1,size=12345,file='/path/to/some/file.jpg')
        
        
        
    def test_serialize(self):
        factory = APIRequestFactory()
        request = factory.get('/comap/api/waypoints/1.json')
        waypoint = Waypoint.objects.get(fid=1)
        serializer = WaypointSerializer([waypoint], many=True, context={'request': request})
        logging.debug(json.dumps(serializer.data, indent=4))