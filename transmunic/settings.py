"""
Django settings for transmunic project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

from email.utils import getaddresses
import environ
import os

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env()
DEBUG = env('DEBUG')
SECRET_KEY = env('SECRET_KEY')
DATABASES = {
    'default': env.db(),
    'readonly': env.db('DATABASERO_URL'),
}
EXPLORER_CONNECTIONS = {'Default': 'readonly'}
EXPLORER_DEFAULT_CONNECTION = 'readonly'

ADMINS = getaddresses([env('DJANGO_ADMINS')])
MANAGERS = ADMINS

SITE_ID = 1

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'lugar.context_processors.info',
            ],
        },
    },
]

ALLOWED_HOSTS = ['*']


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
    'django.contrib.humanize',
    'django.contrib.postgres',

    # 'model_report',
    'sorl.thumbnail',
    # 'pixelfields_smart_selects',
    # 'chartit',
    'mathfilters',
    'explorer',

    'lugar',
    'core',
    'website',
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
LANGUAGE_CODE = 'es-ni'
TIME_ZONE = 'America/Managua'
USE_I18N = True
USE_L10N = True
USE_TZ = True

USE_THOUSAND_SEPARATOR = False
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

CHART_OPTIONS_COLORS = [
    '#2b7ab3',
    '#00a7b2 ',
    '#5A4A42',
    '#D65162',
    '#8B5E3B',
    '#84B73F',
    '#AF907F',
    '#FFE070',
    '#25AAE1']

CHARTS_COLORSCHEME = [
    '#2b7ab3',
    '#00a7b2 ',
    '#5A4A42',
    '#D65162',
    '#8B5E3B',
    '#84B73F',
    '#AF907F',
    '#FFE070',
    '#25AAE1']

CHART_OPTIONS_RESPONSIVE = {
    'rules': [
        {
            'condition': {
                'maxWidth': 540
            },
            'chartOptions': {
                'legend': {
                    'enabled': False
                    }
            }
        },
        {
            'condition': {
                'maxWidth': 720
            },
            'chartOptions': {
                'legend': {
                    'enabled': False
                }
            }
        },
        {
            'condition': {
                'maxWidth': 960
            },
            'chartOptions': {
                'legend': {
                    'enabled': True
                }
            }
        },
        {
            'condition': {
                'maxWidth': 1140
            },
            'chartOptions': {
                'legend': {
                    'enabled': True
                }
            }
        }
        ]
}

CHART_OPTIONS = {
    'title': {'text': u' '},
    'yAxis': {'title': {'text': u'Millones de cordobas'}},
    'xAxis': {'title': {'text': u'Rubros'}},
    'legend': {'enabled': True},
    'colors': CHART_OPTIONS_COLORS,
    'credits': {'enabled': False},
    'plotOptions': {
        'pie': {
            'dataLabels': {
                'enabled': True,
                'format': '{point.percentage:.2f} %'
            },
            'showInLegend': True,
            'depth': 35
        },
        'column': {
            'showInLegend': False,
            'dataLabels': {
                'enabled': False,
                'format': '{point.y:.2f}'},
            'depth': 35
            }
        },
    'tooltip': {
        'pointFormat': '{series.name}: <b>{point.y:.2f} </b>'},
    'responsive': CHART_OPTIONS_RESPONSIVE
}

CHART_OPTIONS_BAR = {
    'legend': {'enabled': False},
}

COLORS_ARRAY = [
    '#37a2da',
    '#314454',
    '#ce8266',
    '#9ee6b7',
    '#ffdb5c',
    '#ff9f7e',
    '#fb7292',
    '#e062ae',
    '#e690d2',
    '#e7bcf3',
    '#9d95f5',
    '#67a0a8',
    '#96bfff',
]

'' # Definiendo url login
LOGIN_URL = '/admin/login/'

try:
    LOCAL_SETTINGS
except NameError:
    try:
        from local_settings import *
    except ImportError:
        pass
