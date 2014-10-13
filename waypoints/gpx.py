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
import gpsbabel, logging, os
from osgeo import ogr
from django.contrib.gis.gdal import DataSource


# Get an instance of a logger
logger = logging.getLogger(__name__)

class GPXProc(object):
    
    def __init__(self, gpx_path):
        logger.debug(os.getcwd())
        self.gpx_path = gpx_path
        logger.debug(self.gpx_path)
        driver = ogr.GetDriverByName('GPX')
        self.ds = driver.Open(self.gpx_path)
        logger.debug('Opening GPX file for reading: %s' % self.ds.name)

    def process_gpx(self):
        logger.debug('Processing gpxfile: %s' % self.gpx_path)
        layer = None
        for lyr in ds:
            logger.debug('Layer "%s": %i %ss' % (lyr.name, len(lyr), lyr.geom_type.name))
            if lyr.name == data_type:
                layer = lyr
                logger.debug('Processing layer: %s' % layer.name)
                break
            else:
                continue
        if layer == None:
            logger.debug("Couldn't find layer matching requested data type. Aborting.")
    
            
