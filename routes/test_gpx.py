'''
Test Harness for GPX Operations

@author: Brian O'Hare
'''

import logging, unittest, sys

from django.test import TestCase
from datetime import datetime
from string import Template
from gpx import GPXProc
from models import TrackPoint

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
  

class GPXTest(TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def testGPXProc(self):
        proc = GPXProc('/home/ubuntu/gpx/waymarkers.gpx')
        proc.process_gpx()
        points = TrackPoint.objects.all()
        self.assertEqual(486, len(points))
        

if __name__ == '__main__':
    unittest.main()



