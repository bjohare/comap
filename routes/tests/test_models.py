import logging, sys
from datetime import datetime
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from ..models import TrackPoint, Route

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class RouteTest(TestCase):
    def setUp(self):
        the_geom = "MULTILINESTRING((-10.86345841795268541 51.21856893786657139, -10.86345397480998187 51.21856535747356531, -10.86344716589865378 51.21856642597708031, -10.86344370986266128 51.21856823220777954, -10.86344671294969899 51.21857034486079385, -10.86345115990679844 51.21857048192958217, -10.86345624274928845 51.21856964697647641, -10.86345862731646683 51.2185695066124822, -10.86345923330451413 51.2185687539405734, -10.86345836256442787 51.21856664373523671, -10.86345655688364609 51.21856559485520677))"
        Route.objects.create(name='Mountain Walk', description='A Mountain Walk', created='2012-05-20 14:10:31', image_file='/image.jpg', user_id=2, group_id=1, the_geom=the_geom)
    
    def testRouteCreation(self):
        time = datetime.strptime('2012-05-20 14:10:31', "%Y-%m-%d %H:%M:%S")
        routes = Route.objects.all()
        route = routes[0]
        logging.debug(route)
        self.assertEquals('Mountain Walk', route.name)
        self.assertEquals(time, route.created)
        route.delete()


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