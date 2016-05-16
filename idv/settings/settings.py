import os

from django.core.exceptions import ImproperlyConfigured

import dj_database_url

from .utils import env_as_bool, env_as_list


# -----------------------------------------------------------------------------
# Environment constants

ENV_DEV = 'dev'
ENV_STAGING = 'staging'
ENV_PROD = 'prod'
_envinronments = [ENV_DEV, ENV_STAGING, ENV_PROD]

# -----------------------------------------------------------------------------
# Load environment settings

IDV_ENVIRONMENT = os.environ['IDV_ENVIRONMENT'].lower()

if IDV_ENVIRONMENT not in _envinronments:
    raise ImproperlyConfigured(
        'Unsupported environment: {}'.format(IDV_ENVIRONMENT)
    )

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
    'idv.collector',
    'idv.mover',
    'idv.sftp',
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

if IDV_ENVIRONMENT == ENV_PROD:
    STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# -----------------------------------------------------------------------------
# Email

EMAIL_HOST = os.getenv('EMAIL_HOSt', 'localhost')
EMAIL_PORT = os.getenv('EMAIL_PORT', 25)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = ''
REPORT_RECIPIENTS = env_as_list('REPORT_RECIPIENTS')
# -----------------------------------------------------------------------------
# S3
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')

# -----------------------------------------------------------------------------
# Customization for development

if IDV_ENVIRONMENT == ENV_DEV:
    INSTALLED_APPS += (
        'django_extensions',
    )
