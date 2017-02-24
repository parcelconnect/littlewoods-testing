# flake8: noqa

from .base import *


INSTALLED_APPS += (
    'django_extensions',
)

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
