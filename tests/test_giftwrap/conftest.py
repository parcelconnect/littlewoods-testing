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


@pytest.fixture
def request_new():
    return GiftWrapRequest.objects.create(
        account_number="A02",
        upi="B" * 13,
        card_message="Newly",
        status=GiftWrapRequestStatus.New.value
    )


@pytest.fixture
def request_failed():
    return GiftWrapRequest.objects.create(
        account_number="A03",
        upi="C" * 13,
        card_message="Deathly",
        status=GiftWrapRequestStatus.Failed.value
    )


@pytest.fixture
def request_error():
    return GiftWrapRequest.objects.create(
        account_number="A04",
        upi="D" * 13,
        card_message="Wrongly",
        status=GiftWrapRequestStatus.Error.value
    )


@pytest.fixture
def request_rejected():
    return GiftWrapRequest.objects.create(
        account_number="A05",
        upi="E" * 13,
        card_message="Rejectedly",
        status=GiftWrapRequestStatus.Rejected.value
    )
