#!/usr/bin/env python
"""
    Copyright (C) 2014  Brian O'Hare

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
import gpsbabel, logging, os, pprint
from osgeo import ogr
from models import TrackPoint
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import OGRGeometry


# Get an instance of a logger
logger = logging.getLogger(__name__)

class GPXProc(object):
    
    def __init__(self, gpx_path):
        logger.debug(os.getcwd())
        self.gpx_path = gpx_path
        logger.debug(self.gpx_path)
       
        self.driver = ogr.GetDriverByName('GPX')
        self.ds = self.driver.Open(self.gpx_path)
       
        logger.debug('Opening GPX file for reading: %s' % self.ds.name)
        

    def process_gpx(self):
        track_points = self.ds.GetLayerByName('track_points')
        count = 0
        for i in range(track_points.GetFeatureCount()):
            feature = track_points.GetFeature(i)
            ele = feature.GetField('ele')
            time = feature.GetField('time')
            ts = time.replace('/', '-')
            geom = feature.GetGeometryRef().ExportToWkt()
            point = GEOSGeometry(geom)
            tp = TrackPoint(ele=ele, time=ts, the_geom=point, user_id=4, route_id=1, group_id=1)
            tp.save()
            logging.debug("Saved TP: %s" % tp)
            count = count + 1
        self.driver = None     
        logging.debug('Saved %d track_points' % count)
          
