# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from .contrib import *

INSTALLED_APPS += (
    'waypoints',
    'routes',
    'api',
    'ui',
)

# root storage for uploaded gpx files
GPX_ROOT = os.path.join(MEDIA_ROOT, 'gpx')

# authentication related
LOGIN_URL = '/comap/login/'
LOGIN_REDIRECT_URL = '/comap/routes/'
