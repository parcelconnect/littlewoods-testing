from .base import *  # noqa

WSGI_APPLICATION = 'idv.wsgi.application'

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

SECURE_SSL_REDIRECT = True
