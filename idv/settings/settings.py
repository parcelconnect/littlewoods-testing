import os

import dj_database_url

from .utils import env_as_bool


# -----------------------------------------------------------------------------
# Base settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '$$fu%@j#c2_vl0xc0c=_it)zxd=h=(+@p2a_i3d63*rk3vk+b&'

ALLOWED_HOSTS = []

DEBUG = env_as_bool('DEBUG')

# -----------------------------------------------------------------------------
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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
        'DIRS': [],
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
