from .base import *  # noqa

WSGI_APPLICATION = 'idv.wsgi.application'

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
