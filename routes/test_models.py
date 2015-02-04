import logging, sys
from datetime import datetime
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from models import TrackPoint, Route

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class RouteTest(TestCase):
    def setUp(self):
        Route.objects.create(name='Mountain Walk', description='A Mountain Walk', created='2012-05-20 14:10:31', image_path='/image.jpg', user_id=2, group_id=1)
    
    def testRouteCreation(self):
        time = datetime.strptime('2012-05-20 14:10:31', "%Y-%m-%d %H:%M:%S")
        routes = Route.objects.all()
        route = routes[0]
        logging.debug(route)
        self.assertEquals(2, route.fid)
        self.assertEquals('Mountain Walk', route.name)
        self.assertEquals(time, route.created)


class TrackPointTest(TestCase):
    def setUp(self):
        point = GEOSGeometry('POINT (-7.102992720901966 54.326739795506001)')
        TrackPoint.objects.create(ele=223.45, time='2012-05-20 14:10:31', the_geom = point, route_id=1)
    
    def testTrackPointCreation(self):
        geom = GEOSGeometry('POINT (-7.102992720901966 54.326739795506001)')
        points = TrackPoint.objects.all()
        track_point = points[0]
        logging.debug(track_point)
        self.assertEquals(geom, track_point.the_geom)
        

     

    
if __name__ == '__main__':
    unittest.main()