import json

import pytest
import requests
import responses

from idv.giftwrap import ifs


@pytest.fixture
def client_config():
    return {
        'base_url': 'https://fastway.ie',
        'username': 'foo',
        'password': 'bar',
        'test_mode': True
    }


class TestIFSClientInit:

    def test_init_sets_session(self, client_config):
        client = ifs.Client(**client_config)
        assert isinstance(client._session, requests.Session)

    def test_create_session_sets_up_basicauth(self, client_config):
        session = ifs.Client.create_session('foo', 'bar')
        assert isinstance(session, requests.Session)
        assert session.auth == ('foo', 'bar')
        assert session.headers['referer'] == 'Littlewoods'
        assert session.headers['User-Agent'] == 'Littlewoods Gift Wrapping'


class TestIFSClientRequestGiftWrap:

    url = 'https://fastway.ie/webhooks/giftwrap/'

    @pytest.fixture
    def ifs_client(self, client_config):
        return ifs.Client(**client_config)

    @pytest.fixture
    def address(self):
        return {
            "address1": "7 Stanley Studios",
            "address2": "Park Walk",
            "town": "Wexford Town",
            "county": "Wexford",
            "name": "Mr John Smith",
            "phone_number": "393939393"
        }

    @responses.activate
    def test_it_returns_true_when_response_ok(self, ifs_client):
        responses.add(responses.POST, self.url, json={"status": "ok"})
        ifs_client.request_gift_wrap('MadeUpUPINum')

        assert len(responses.calls) == 1
        request_performed = responses.calls[0].request
        assert request_performed.headers['Content-Type'] == 'application/json'
        assert request_performed.headers['referer'] == 'Littlewoods'
        assert json.loads(request_performed.body) == {
            "giftwrap": {
                "mode": "test",
                "upi": ['MadeUpUPINum'],
            }
        }

    @responses.activate
    def test_it_sends_address_when_new_address_is_given(
            self, ifs_client, address):
        responses.add(responses.POST, self.url, json={"status": "ok"})
        ifs_client.request_gift_wrap('MadeUpUPINum', address)

        assert len(responses.calls) == 1
        request_performed = responses.calls[0].request
        assert json.loads(request_performed.body) == {
            "giftwrap": {
                "mode": "test",
                "upi": ['MadeUpUPINum'],
                "receiver": {
                    "add1": "7 Stanley Studios",
                    "add2": "Park Walk",
                    "add3": "Wexford Town",
                    "add4": "Wexford",
                    "add5": "",
                    "add6": "Republic of Ireland",
                    "contact": "Mr John Smith",
                    "phone": "393939393"
                }
            }
        }

    @responses.activate
    def test_it_raises_TooLateError_when_status_is_fail(self, ifs_client):
        responses.add(responses.POST, self.url, json={"status": "fail"})

        with pytest.raises(ifs.TooLateError):
            ifs_client.request_gift_wrap('FoobarUPI')

        assert len(responses.calls) == 1

    @responses.activate
    def test_post_connection_error_raises(self, ifs_client):
        with pytest.raises(ifs.IFSAPIError):
            # responses will raise a connection error here
            ifs_client.request_gift_wrap(self.url)

        assert len(responses.calls) == 1
