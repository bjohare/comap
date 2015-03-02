"""
Django settings for comap project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'os+i+s__!u8j#&!kq1%aj2s23++77)dqd%w$2kg53#y6rqu2+l'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates/'),
    'api/templates/',
    'routes/templates/',)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.request",
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",  
)

ALLOWED_HOSTS = []

# authentication related
LOGIN_URL = '/comap/login/'
LOGIN_REDIRECT_URL = '/comap/routes/'


# Application definition

DEFAULT_APPS = (
    'grappelli',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
)

THIRD_PARTY_APPS = (
    'rest_framework',
    'rest_framework_gis',
    'imagekit',
)

LOCAL_APPS = (
    'waypoints',
    'routes',
    'api',
)

INSTALLED_APPS = DEFAULT_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',), 
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.authentication.SessionAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',)
}

ROOT_URLCONF = 'comap.urls'

WSGI_APPLICATION = 'comap.wsgi.application'

# session settings
SESSION_COOKIE_NAME='comap_sessionid'
SESSION_COOKIE_DOMAIN='cloughjordan.ie'
SESSION_COOKIE_PATH='/comap'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
# django.db.backends.postgresql_psycopg2
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'waymarkers',
        'OPTIONS': {
            'options': '-c search_path=waymarkers,public'
        },
        'USER': 'gis',
        'PASSWORD': 'al1ngton',
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/comap/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    'routes/static/routes/',
    'waypoints/static/waypoints/'
)

MEDIA_URL = '/comap/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# root storage for uploaded gpx files
GPX_ROOT = os.path.join(BASE_DIR, 'media/gpx/')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
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
            'handlers':['file'],
            'propagate': True,
            'level':'DEBUG',
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
    }
}

# Grappelli Settings

GRAPPELLI_ADMIN_TITLE = 'CoMap Administration'
