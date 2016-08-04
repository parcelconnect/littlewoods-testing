from django.conf import settings

from .client import Client


def get_client_from_settings():
    if not settings.FASTWAY_API_KEY:
        raise ValueError('Cannot create Fastway Client from settings. '
                         'FASTWAY_API_KEY is not set.')
    if not settings.FASTWAY_API_ENDPOINT:
        raise ValueError('Cannot create Fastway Client from settings. '
                         'FASTWAY_API_ENDPOINT is not set.')
    return Client(
        base_url=settings.FASTWAY_API_ENDPOINT,
        api_key=settings.FASTWAY_API_KEY
    )
