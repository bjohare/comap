'''
Test Harness for GPX Operations

@author: Brian O'Hare
'''

import logging, unittest, sys

from django.test import TestCase
from datetime import datetime
from string import Template
from gpx import GPXProc
from models import TrackPoint, Route

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  

class GPXTest(TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.route = Route.objects.create(name='A Test Route', description='A Test Description', created='2012-05-20 14:10:31', image_path='/image.jpg', user_id=2, group_id=1)
        
    def testGPXProc(self):
        proc = GPXProc('/home/ubuntu/gpx/waymarkers.gpx', self.route)
        proc.process_gpx()
        points = TrackPoint.objects.all()
        self.assertEqual(486, len(points))
        

if __name__ == '__main__':
    unittest.main()



