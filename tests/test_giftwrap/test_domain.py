import json

import pytest
import responses

from idv.giftwrap.domain import request_gift_wrap
from idv.giftwrap.models import GiftWrapRequest


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

    @pytest.fixture
    def client_settings(self, settings):
        settings.IFS_API_ENDPOINT = "https://fastway.ie"
        settings.IFS_API_USERNAME = "test"
        settings.IFS_API_PASSWORD = "me"
        settings.IFS_API_TEST_MODE = True

    @responses.activate
    def test_it_sends_address_when_new_address_is_given(
            self, gift_wrap_request, client_settings):
        responses.add(responses.POST, self.url, json={"status": "ok"})
        request_gift_wrap(gift_wrap_request)

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
            "add6": "Republic of Ireland",
            "contact": "Mr John Smith",
            "phone": "393939393"
        }
