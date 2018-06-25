# pylint: disable=W0614
# pylint: disable=C0111

# flake8: noqa

from .base import *

DEBUG = True

INSTALLED_APPS += (
    'django_extensions',
)

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend'
)
