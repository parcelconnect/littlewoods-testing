import json
from unittest import mock

import pytest
import responses

from idv.giftwrap import domain, ifs
from idv.giftwrap.models import GiftWrapRequest
from idv.giftwrap.types import GiftWrapRequestStatus


@pytest.mark.django_db
class TestRequestGiftWrap:

    url = 'https://fastway.ie/webhooks/giftwrap/'

    @pytest.fixture
    def gift_wrap_request(self):
        return GiftWrapRequest(
            account_number=123,
            upi="ABC123",
            divert_address1="7 Stanley Studios",
            divert_address2="Park Walk",
            divert_town="Wexford Town",
            divert_county="Wexford",
            divert_contact_name="Mr John Smith",
            divert_contact_number="393939393"
        )

    @responses.activate
    @pytest.mark.django_db
    def test_it_sends_address_when_new_address_is_given(
            self, gift_wrap_request, client_settings):
        responses.add(responses.POST, self.url, json={"status": "ok"})
        domain.request_gift_wrap(gift_wrap_request)

        assert len(responses.calls) == 1
        request_performed = responses.calls[0].request
        response = json.loads(request_performed.body)

        assert response["giftwrap"]["upi"] == ['ABC123']
        assert response["giftwrap"]["receiver"] == {
            "add1": "7 Stanley Studios",
            "add2": "Park Walk",
            "add3": "Wexford Town",
            "add4": "Wexford",
            "add5": "",
            "add6": "Ireland",
            "contact": "Mr John Smith",
            "phone": "393939393"
        }

    @mock.patch.object(
        domain.ifs.Client,
        'request_gift_wrap',
        return_value=True
    )
    @responses.activate
    def test_it_sets_and_returns_success_status_when_post_returns_true(
            self, mock_client_method, client_settings, gift_wrap_request):
        result = domain.request_gift_wrap(gift_wrap_request)
        assert len(mock_client_method.mock_calls) == 1
        assert result == GiftWrapRequestStatus.Success.value

    @mock.patch.object(
        domain.ifs.Client,
        'request_gift_wrap',
        side_effect=ifs.TooLateError('Late. Yes')
    )
    @responses.activate
    def test_it_sets_and_returns_failed_status_when_post_raises_too_late(
            self, mock_client_method, client_settings, gift_wrap_request):
        result = domain.request_gift_wrap(gift_wrap_request)
        assert len(mock_client_method.mock_calls) == 1
        assert result == GiftWrapRequestStatus.Failed.value

    @mock.patch.object(
        domain.ifs.Client,
        'request_gift_wrap',
        side_effect=ifs.IFSAPIError('Catastrophe')
    )
    @responses.activate
    def test_it_sets_and_returns_failed_status_when_post_raises_error(
            self, mock_client_method, client_settings, gift_wrap_request):
        result = domain.request_gift_wrap(gift_wrap_request)
        assert len(mock_client_method.mock_calls) == 1
        assert result == GiftWrapRequestStatus.Error.value
