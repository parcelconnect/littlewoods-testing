import pytest

from idv.giftwrap.models import GiftWrapRequest, GiftWrapRequestStatus


@pytest.fixture
def client_settings(settings):
    settings.IFS_API_ENDPOINT = "https://fastway.ie"
    settings.IFS_API_USERNAME = "test"
    settings.IFS_API_PASSWORD = "me"
    settings.IFS_API_TEST_MODE = True
    return settings


@pytest.fixture
def request_success():
    return GiftWrapRequest.objects.create(
        account_number="A01",
        upi="A" * 13,
        card_message="Lovely",
        status=GiftWrapRequestStatus.Success.value
    )
