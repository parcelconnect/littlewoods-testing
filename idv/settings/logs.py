import os
import sys

from .django import INSTALLED_APPS

SHELL = 'shell' in sys.argv
LOG_HANDLERS = ['console']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        }
    }
}

RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_DSN'),
    'ignore_exceptions': ('*',) if SHELL else ()
}

if RAVEN_CONFIG['dsn']:
    INSTALLED_APPS += [
        'raven.contrib.django.raven_compat',
    ]
    LOGGING['handlers']['sentry'] = {
        'level': 'ERROR',
        'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
    }

LOGGING['loggers'] = {
    'django': {
        'handlers': LOG_HANDLERS,
        'level': 'INFO',
        'propagate': False,
    },
    'idv': {
        'handlers': LOG_HANDLERS,
        'level': 'INFO',
        'propagate': False,
    },
}
