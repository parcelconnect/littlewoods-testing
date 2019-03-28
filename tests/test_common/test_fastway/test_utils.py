import pytest

from idv.common.fastway.utils import get_client_from_settings


class TestGetClientFromSettings:

    @pytest.fixture
    def settings(self, settings):
        settings.FASTWAY_API_KEY = 'Something'
        settings.FASTWAY_API_ENDPOINT = 'Something'
        return settings

    def test_returns_valid_client_when_settings_set(self, settings):
        client = get_client_from_settings()

        assert client is not None

    def test_raises_value_error_when_no_fastway_api_key(self, settings):
        settings.FASTWAY_API_KEY = None

        with pytest.raises(ValueError) as exc:
            get_client_from_settings()

        expected_error = ('Cannot create Fastway Client from settings. '
                          'FASTWAY_API_KEY is not set.')

        assert expected_error in str(exc)

    def test_raises_value_error_when_no_fastway_api_endpoint(self, settings):
        settings.FASTWAY_API_ENDPOINT = None

        with pytest.raises(ValueError) as exc:
            get_client_from_settings()

        expected_error = ('Cannot create Fastway Client from settings. '
                          'FASTWAY_API_ENDPOINT is not set.')

        assert expected_error in str(exc)
