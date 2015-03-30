import logging, sys, pdb

from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import GEOSGeometry
from django.core.files.uploadedfile import SimpleUploadedFile

from routes.models import Route
from models import Waypoint, WaypointMedia

from api.views import WaypointMediaViewSet

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class WaypointMediaViewSetTest(TestCase):
    
    
    def setUp(self):
        self.factory = APIRequestFactory(format='multipart')
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
    
    
    def testCreate(self):
        logging.debug('In testCreate')
        video = SimpleUploadedFile("file.mp4", "file_content", content_type="video/mp4")
        request = self.factory.post('/api/waypoints/media.json', {'media_file':  video, 'group_id': 1, 'waypoint_id': 1, 'route_id': 1}, format='multipart')
        force_authenticate(request, user=self.user)
        view = WaypointMediaViewSet.as_view({'post':'create'})
        response = view(request)
        media = WaypointMedia.objects.get(fid=response.data['fid'])
        #pdb.set_trace()
        media.delete()
        
        

class WaypointMediaApiTestCase(APITestCase):
    pass

        