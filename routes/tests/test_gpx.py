'''
Test Harness for GPX Operations

@author: Brian O'Hare
'''

import logging, unittest, sys, os

from django.test import TestCase
from datetime import datetime
from string import Template
from ..gpx import GPXProc
from ..models import TrackPoint, Route

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  

class GPXTest(TestCase):
    
    def setUp(self):
        the_geom = "MULTILINESTRING((-10.86345841795268541 51.21856893786657139, -10.86345397480998187 51.21856535747356531, -10.86344716589865378 51.21856642597708031, -10.86344370986266128 51.21856823220777954, -10.86344671294969899 51.21857034486079385, -10.86345115990679844 51.21857048192958217, -10.86345624274928845 51.21856964697647641, -10.86345862731646683 51.2185695066124822, -10.86345923330451413 51.2185687539405734, -10.86345836256442787 51.21856664373523671, -10.86345655688364609 51.21856559485520677))"
        self.route = Route.objects.create(name='A Test Route', description='A Test Description', created='2012-05-20 14:10:31', image_file='/image.jpg', user_id=2, group_id=1, the_geom=the_geom)
        
    def testGPXProc(self):
        path = os.path.dirname(os.path.realpath(__file__))
        gpx_path = path + '/test.gpx'
        proc = GPXProc(gpx_path)
        proc.get_track()
        proc.save_trackpoints(self.route.fid)
        points = TrackPoint.objects.all()
        self.assertEqual(30, len(points))



