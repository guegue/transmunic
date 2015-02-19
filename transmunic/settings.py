"""
Django settings for transmunic project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from local_settings import *
import os
import dj_database_url

from django.conf import global_settings as DJANGO_DEFAULT

DEBUG = 'DEBUG' in os.environ and not os.environ['DEBUG'] == 'False'
TEMPLATE_DEBUG = DEBUG

#BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=*2w4v6%9wib742a3hr!&a0h2%a_x2pp7k6svha1@@1g0y#q(s'
SITE_ID = 1

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

TEMPLATE_DIRS = ('templates', )

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',

    #'sorl.thumbnail',
    'pixelfields_smart_selects',

    'lugar',
    'core',
    'website',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'transmunic.forcelanguage.ForceDefaultLanguageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'transmunic.urls'

WSGI_APPLICATION = 'transmunic.wsgi.application'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Managua'
USE_I18N = True
USE_L10N = True
USE_TZ = True

USE_THOUSAND_SEPARATOR = True
DECIMAL_SEPARATOR = '.'
THOUSAND_SEPARATOR = ','
NUMBER_GROUPING = 3

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(SITE_ROOT, 'media'))
STATIC_ROOT = os.environ.get('STATIC_ROOT', os.path.join(SITE_ROOT, 'static'))

try:
   LOCAL_SETTINGS
except NameError:
    try:
       from local_settings import *
    except ImportError:
        pass

