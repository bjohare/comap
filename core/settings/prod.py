from __future__ import absolute_import

from .project import *  # NOQA

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['']

# Comment if you are not running behind proxy
# USE_X_FORWARDED_HOST = True

# Set debug to false for production
DEBUG = False


DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'waymarkers',
        'OPTIONS': {
            'options': '-c search_path=waymarkers,public'
        },
        'CONN_MAX_AGE': None,
        'USER': 'gis',
    }
}

# session settings
SESSION_COOKIE_NAME = 'comap_sessionid'
SESSION_COOKIE_DOMAIN = 'waymarkers.org'
SESSION_COOKIE_PATH = '/comap'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

MEDIA_URL = '/comap/media/'
MEDIA_ROOT = '/home/waymarkers/media' 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
