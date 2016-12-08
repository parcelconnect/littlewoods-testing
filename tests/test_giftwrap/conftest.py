import pytest


@pytest.fixture
def client_settings(settings):
    settings.IFS_API_ENDPOINT = "https://fastway.ie"
    settings.IFS_API_USERNAME = "test"
    settings.IFS_API_PASSWORD = "me"
    settings.IFS_API_TEST_MODE = True
    return settings
