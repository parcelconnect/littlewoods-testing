import os

from .settings import INSTALLED_APPS

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

RAVEN_CONFIG = {'dsn': os.environ.get('RAVEN_DSN')}

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
