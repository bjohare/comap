import logging, sys
from datetime import datetime
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry

from models import Waypoint

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


class WaypointTest(TestCase):
    def setUp(self):
        point = GEOSGeometry('POINT (-7.102992720901966 54.326739795506001)')
        Waypoint.objects.create(name='Ballycapple Castle', description='Some descriptive text',
                                elevation=223.45, date='2012-05-20 14:10:31', the_geom = point, route_id=1)
    
    def testTrackPointCreation(self):
        geom = GEOSGeometry('POINT (-7.102992720901966 54.326739795506001)')
        points = Waypoint.objects.all()
        waypoint = points[0]
        logging.debug(waypoint)
        self.assertEquals(geom, waypoint.the_geom)
    
if __name__ == '__main__':
    unittest.main()