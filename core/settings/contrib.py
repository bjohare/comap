# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .base import *  # NOQA

# Extra installed apps
INSTALLED_APPS += (
    # any 3rd party apps
    'rest_framework',
    'rest_framework_gis',
    'rest_framework.authtoken',
    'imagekit',
    'django_nose',
)

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication', 'rest_framework.authentication.TokenAuthentication'),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'api.renderers.ComapApiRenderer',
    ),
}
