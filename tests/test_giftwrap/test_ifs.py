import json

import pytest
import requests
import responses
from django.test import TestCase, override_settings

from idv.giftwrap import ifs


@pytest.fixture
def client_config():
    return {
        'base_url': 'https://fastway.ie',
        'username': 'foo',
        'password': 'bar',
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
                "upi": ['MadeUpUPINum049'],
            }
        }

    @responses.activate
    def test_it_sets_test_mode_when_set(self, client_config):
        responses.add(responses.POST, self.url, json={"status": "ok"})
        client_config['test_mode'] = True
        ifs_client = ifs.Client(**client_config)
        ifs_client.request_gift_wrap('MadeUpUPINum')

        assert len(responses.calls) == 1
        request_performed = responses.calls[0].request
        assert json.loads(request_performed.body) == {
            "giftwrap": {
                "mode": "test",
                "upi": ['MadeUpUPINum049'],
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
                "upi": ['MadeUpUPINum049'],
                "receiver": {
                    "add1": "7 Stanley Studios",
                    "add2": "Park Walk",
                    "add3": "Wexford Town",
                    "add4": "Wexford",
                    "add5": "",
                    "add6": "Ireland",
                    "contact": "Mr John Smith",
                    "phone": "393939393"
                }
            }
        }

    @responses.activate
    def test_it_raises_apierror_when_post_raises_connection_error(
            self, ifs_client):
        with pytest.raises(ifs.IFSAPIError):
            ifs_client.request_gift_wrap('FoobarUPI')

        assert len(responses.calls) == 1

    @responses.activate
    def test_it_raises_apierror_when_post_returns_non_200_status(
            self, ifs_client):
        responses.add(responses.POST, self.url, status=500,
                      json={"status": "ok"})

        with pytest.raises(ifs.IFSAPIError):
            # responses will raise a connection error here
            ifs_client.request_gift_wrap(self.url)

        assert len(responses.calls) == 1

    @responses.activate
    def test_it_raises_TooLateError_when_status_is_fail(self, ifs_client):
        responses.add(responses.POST, self.url, json={"status": "fail"})

        with pytest.raises(ifs.TooLateError):
            ifs_client.request_gift_wrap('FoobarUPI')

        assert len(responses.calls) == 1

    @responses.activate
    def test_it_raises_apierror_when_post_returns_non_ok_status(
            self, ifs_client):
        responses.add(responses.POST, self.url, status=200,
                      json={"status": "oh no!"})

        with pytest.raises(ifs.IFSAPIError) as exc:
            # responses will raise a connection error here
            ifs_client.request_gift_wrap(self.url)

        expected_error = '[IFS]: response status value not "ok": oh no!'

        assert len(responses.calls) == 1
        assert expected_error in str(exc)


class TestGetClientFromSettings(TestCase):

    @override_settings(IFS_API_ENDPOINT='something',
                       IFS_API_USERNAME='something',
                       IFS_API_PASSWORD='something')
    def test_returns_client_when_settings_valid(self):
        client = ifs.get_client_from_settings()

        assert client is not None

    @override_settings(IFS_API_ENDPOINT=None,
                       IFS_API_USERNAME='something',
                       IFS_API_PASSWORD='something')
    def test_raises_value_error_when_endpoint_is_invalid(self):
        with pytest.raises(ValueError) as exc:
            ifs.get_client_from_settings()

        expected_error = ('Cannot create IFS client from settings. '
                          'IFS_API_ENDPOINT is not set')

        assert expected_error in str(exc)

    @override_settings(IFS_API_ENDPOINT='something',
                       IFS_API_USERNAME=None,
                       IFS_API_PASSWORD='something')
    def test_raises_value_error_when_username_is_invalid(self):
        with pytest.raises(ValueError) as exc:
            ifs.get_client_from_settings()

        expected_error = ('Cannot create IFS client from settings. '
                          'IFS_API_USERNAME is not set')

        assert expected_error in str(exc)

    @override_settings(IFS_API_ENDPOINT='something',
                       IFS_API_USERNAME='something',
                       IFS_API_PASSWORD=None)
    def test_raises_value_error_when_password_is_invalid(self):
        with pytest.raises(ValueError) as exc:
            ifs.get_client_from_settings()

        expected_error = ('Cannot create IFS client from settings. '
                          'IFS_API_PASSWORD is not set')

        assert expected_error in str(exc)
