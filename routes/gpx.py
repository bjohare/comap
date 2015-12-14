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
import logging, os, pprint
from osgeo import ogr, gdal
from models import TrackPoint, Route
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.gdal import OGRGeometry

# Get an instance of a logger
logger = logging.getLogger(__name__)

# enable osgeo exceptions
gdal.UseExceptions()

class GPXProc:

    def __init__(self, gpx_path):
        self.gpx_path = gpx_path
        self.driver = ogr.GetDriverByName('GPX')
        self.ds = self.driver.Open(self.gpx_path)

        logger.debug('Opening GPX file for reading: %s' % self.ds.name)


    def get_track(self):
        """ Gets the track layer as a GEOSGeometry"""
        tracks_layer = self.ds.GetLayerByName('tracks')
        track_feature = tracks_layer.GetFeature(0)
        geom = track_feature.GetGeometryRef().ExportToWkt()
        line = GEOSGeometry(geom)
        return line

    def update_trackpoints(self, route_id):
        logger.debug('Updating trackpoints for route with id: {0}'.format(route_id))
        # delete existing trackpoints for this route..
        TrackPoint.objects.filter(route_id=route_id).delete()
        points = []
        track_points = self.ds.GetLayerByName('track_points')
        count = 0
        for i in range(track_points.GetFeatureCount()):
            # this needs to be tidied up to account for missing field values etc..
            feature = track_points.GetFeature(i)
            ele = feature.GetField('ele')
            time = feature.GetField('time')
            ts = None
            if (time != None):
                ts = time.replace('/', '-')
            geom = feature.GetGeometryRef().ExportToWkt()
            point = GEOSGeometry(geom)
            tp = TrackPoint(ele=ele, time=ts, the_geom=point, route_id=route_id)
            tp.save()
            logging.debug("Saved TP: %s" % tp)
            count = count + 1
        self.driver = None
        logging.debug('Saved %d track_points' % count)

    def save_trackpoints(self, route_id):
        """Saves the TrackPoints to the database"""
        points = []
        track_points = self.ds.GetLayerByName('track_points')
        count = 0
        for i in range(track_points.GetFeatureCount()):
            # this needs to be tidied up to account for missing field values etc..
            feature = track_points.GetFeature(i)
            ele = feature.GetField('ele')
            time = feature.GetField('time')
            ts = None
            if (time != None):
                ts = time.replace('/', '-')
            geom = feature.GetGeometryRef().ExportToWkt()
            point = GEOSGeometry(geom)
            tp = TrackPoint(ele=ele, time=ts, the_geom=point, route_id=route_id)
            tp.save()
            logging.debug("Saved TP: %s" % tp)
            count = count + 1
        self.driver = None
        logging.debug('Saved %d track_points' % count)

