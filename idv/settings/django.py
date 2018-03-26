import os

import dj_database_url

from .utils import env_as_bool, env_as_list

# -----------------------------------------------------------------------------
# Base settings

PROJECT_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))

BASE_DIR = os.path.dirname(os.path.join(PROJECT_PATH, '..'))

SECRET_KEY = '$$fu%@j#c2_vl0xc0c=_it)zxd=h=(+@p2a_i3d63*rk3vk+b&'

ALLOWED_HOSTS = ['*']

STATIC_ROOT = os.environ.get('STATIC_ROOT', 'staticfiles')

DEBUG = env_as_bool('DEBUG', default=False)

# -----------------------------------------------------------------------------
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'idv.common',
    'idv.collector',
    'idv.mover',
    'idv.sftp',
    'idv.tracker',
    'idv.giftwrap',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'idv.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_PATH, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'idv.wsgi.application'

# -----------------------------------------------------------------------------
# Database

DATABASES = {
    'default': dj_database_url.config()
}

# -----------------------------------------------------------------------------
# Password validation

VALIDATOR_PATH = 'django.contrib.auth.password_validation.{}'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': VALIDATOR_PATH.format('UserAttributeSimilarityValidator')},
    {'NAME': VALIDATOR_PATH.format('MinimumLengthValidator')},
    {'NAME': VALIDATOR_PATH.format('CommonPasswordValidator')},
    {'NAME': VALIDATOR_PATH.format('NumericPasswordValidator')},
]

# -----------------------------------------------------------------------------
# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# -----------------------------------------------------------------------------
# Static files

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

# -----------------------------------------------------------------------------
# Email

EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = os.getenv('EMAIL_PORT', 25)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = 'support@fastway.ie'
REPORT_RECIPIENTS = env_as_list('REPORT_RECIPIENTS')
UPI_REPORT_RECIPIENTS = env_as_list('UPI_REPORT_RECIPIENTS')

# -----------------------------------------------------------------------------
# S3

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')

# -----------------------------------------------------------------------------
# Whitelisted proxy to use when uploading files to the LW SFTP.

HTTP_PROXY = {
    'host': os.getenv('HTTP_PROXY_HOST'),
    'port': os.getenv('HTTP_PROXY_PORT'),
    'username': os.getenv('HTTP_PROXY_USERNAME'),
    'password': os.getenv('HTTP_PROXY_PASSWORD'),
}

# -----------------------------------------------------------------------------
# Customization for development

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'idv': {
            'handlers': ['console'],
            'level': os.environ.get('IDV_LOG_LEVEL', 'INFO'),
        }
    }
}

# -----------------------------------------------------------------------------
# Mover settings

WHITELISTED_EXTENSIONS = set([
    'jpg', 'jpeg', 'gif', 'pdf',
    'png', 'bmp', 'tiff', 'tif'
])


# -----------------------------------------------------------------------------
# Fastway settings

FASTWAY_API_ENDPOINT = os.environ.get('FASTWAY_API_ENDPOINT')
FASTWAY_API_KEY = os.environ.get('FASTWAY_API_KEY')

# -----------------------------------------------------------------------------
# Gift Wrapping settings

GIFT_WRAPPING_REQUEST_NOTIFICATION_EMAILS = env_as_list(
    'GIFT_WRAPPING_REQUEST_NOTIFICATION_EMAIL'
)

IFS_API_ENDPOINT = "https://sombrero.ifsconnect.net"
IFS_API_USERNAME = os.environ.get('IFS_API_USERNAME')
IFS_API_PASSWORD = os.environ.get('IFS_API_PASSWORD')
IFS_API_TEST_MODE = env_as_bool('IFS_API_TEST_MODE', default=False)

SPECIAL_DATE_NAME = os.environ.get('SPECIAL_DATE_NAME', '')

SPECIAL_DATE_IMAGE = {
    'Valentine\'s Day': 'img/lwi-valentine-wrap-bg.png',
    'Christmas': 'img/lwi-gift-wrapping-bg.png',
    'Mother\'s Day': 'img/lwi-mother-wrap-bg.png',
    'Father\'s Day': 'img/lwi-father-wrap-bg.png',
}

RUN_REPORT_FROM_DATE = '2017 05 02 00:00:00 {}'.format(TIME_ZONE)
