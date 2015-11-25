# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .project import *  # NOQA

# Set debug to True for development
DEBUG = True
LOGGING_OUTPUT_ENABLED = DEBUG
LOGGING_LOG_SQL = DEBUG
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = []


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'cloughjordan',
        'OPTIONS': {
            'options': '-c search_path=comap,public'
        },
        'CONN_MAX_AGE': None,
        'USER': 'gis',
    }
}


TEMPLATE_DIRS = (
    ABS_PATH('templates'),
    'api/templates/',
    'ui/templates/',)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching while in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'INFO',
        },
        'waypoints': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'api': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'routes': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'comap': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

MEDIA_URL = '/comap/media/'
MEDIA_ROOT = ABS_PATH('media')

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
