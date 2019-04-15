import pytest
from django.test import TestCase, override_settings

from idv.common.fastway.utils import get_client_from_settings


class TestGetClientFromSettings(TestCase):

    @override_settings(FASTWAY_API_KEY='Something',
                       FASTWAY_API_ENDPOINT='Something')
    def test_returns_valid_client_when_settings_set(self):
        client = get_client_from_settings()

        assert client is not None

    @override_settings(FASTWAY_API_KEY=None, FASTWAY_API_ENDPOINT='Something')
    def test_raises_value_error_when_no_fastway_api_key(self):
        with pytest.raises(ValueError) as exc:
            get_client_from_settings()

        expected_error = ('Cannot create Fastway Client from settings. '
                          'FASTWAY_API_KEY is not set.')

        assert expected_error in str(exc)

    @override_settings(FASTWAY_API_KEY='Something', FASTWAY_API_ENDPOINT=None)
    def test_raises_value_error_when_no_fastway_api_endpoint(self):
        with pytest.raises(ValueError) as exc:
            get_client_from_settings()

        expected_error = ('Cannot create Fastway Client from settings. '
                          'FASTWAY_API_ENDPOINT is not set.')

        assert expected_error in str(exc)
