import logging, sys
from datetime import datetime
from django.test import TestCase
from django.core.files import File
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.auth.models import User, Group

from routes.models import Route
from models import Waypoint, WaypointMedia

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class WaypointTest(TestCase):
    def setUp(self):
        linestring = GEOSGeometry('MULTILINESTRING((-7.10411262698471 54.3239101488143,-7.10412142798305 54.3239141721278,-7.10410986095667 54.3239162676036,-7.10410818457604 54.3238997552544,-7.1040909178555 54.3239010125399))')
        Route.objects.create(name='TestRoute', description='Test Route Description', the_geom=linestring, user_id=2, group_id=1, created='2012-05-20 14:10:31', image_file='/image.jpg')
        point = GEOSGeometry('POINT (-7.102992720901966 54.326739795506001)')
        Waypoint.objects.create(name='Ballycapple Castle', description='Some descriptive text',
                                elevation=223.45, created='2012-05-20 14:10:31', the_geom = point, route_id=1)
    
    def testTrackPointCreation(self):
        geom = GEOSGeometry('POINT (-7.102992720901966 54.326739795506001)')
        points = Waypoint.objects.all()
        waypoint = points[0]
        logging.debug(waypoint)
        self.assertEquals(geom, waypoint.the_geom)
        
       
class WaypointMediaTest(TestCase):
    def setUp(self):
        linestring = GEOSGeometry('MULTILINESTRING((-7.10411262698471 54.3239101488143,-7.10412142798305 54.3239141721278,-7.10410986095667 54.3239162676036,-7.10410818457604 54.3238997552544,-7.1040909178555 54.3239010125399))')
        Route.objects.create(fid=22,name='TestRoute', description='Test Route Description', the_geom=linestring, user_id=2, group_id=1, created='2012-05-20 14:10:31', image_file='/image.jpg')
        point = GEOSGeometry('POINT (-7.102992720901966 54.326739795506001)')
        Waypoint.objects.create(name='Ballycapple Castle', description='Some descriptive text',
                                elevation=223.45, created='2012-05-20 14:10:31', the_geom = point, route_id=22)
        f = open('/home/ubuntu/www/waymarkers/comap/media/lakeside.jpg')
        self.file = File(f)  
    
    
    def testCreateWaypointMedia(self):
        logging.debug('In create waypoint test..')
        group = Group.objects.create(name='Monaghan Ramblers')
        user = User.objects.create_user('frank','frank@frank.com','frank')
        user.groups = [group]
        route = Route.objects.get(fid=22)
        self.assertEqual(route.fid, 22)
        self.assertEqual(route.name, 'TestRoute')
        waypoint = route.waypoints.get()
        self.assertEqual(waypoint.name, 'Ballycapple Castle')
        wpm = WaypointMedia.objects.create(fid=1, content_type='image', filename='lakeside.jpg',size=20, file=self.file, waypoint=waypoint,created=datetime.now())
        wpm.save()
        self.assertEquals(wpm.file.url, '/comap/media/1/22/waypoints/image/lakeside.jpg')
        logging.debug('File url: {0}'.format(wpm.file.url))
        
        # cleanup by deleting the file
        wpm.delete()
        
    def testUpdateWaypointMedia(self):
        logging.debug('In update waypoint test..')
    
    def testDeleteWaypointMedia(self):
        logging.debug('In delete waypoint test..')
    
    def tearDown(self):
        logging.debug('In tear down')
        
    
if __name__ == '__main__':
    unittest.main()