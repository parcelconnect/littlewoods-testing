import json
from unittest.mock import patch

import pytest
import responses
from requests.exceptions import RequestException

from idv.common.fastway.client import Client
from idv.common.fastway.exceptions import FastwayAPIError


class TestClient:

    @patch('requests.request')
    def test_raises_fastway_api_error_when_request_exception(
            self, mock_request):
        mock_request.side_effect = [RequestException('Request Invalid')]

        client = Client('base_url', 'api_key')

        with pytest.raises(FastwayAPIError) as exc:
            client._request('post', 'base_url')

        expected_error = ("Error connecting to the Fastway API: "
                          "RequestException('Request Invalid')")

        assert expected_error in str(exc)

    @responses.activate
    def test_raises_fastway_api_error_message_when_response_not_200(self):
        expected_response = '{"error": "Field required."}'
        responses.add(responses.POST,
                      'http://localhost/v2/base_url?api_key=api_key',
                      json=json.loads(expected_response), status=400)

        client = Client('http://localhost', 'api_key')

        with pytest.raises(FastwayAPIError) as exc:
            client._request('post', 'base_url')

        print(exc)

        assert str(expected_response) in str(exc)

    def test_returns_empty_string_when_status_cannot_be_translated(self):
        client = Client('base_url', 'api_key')

        status = client._translate_status('Invalid')

        assert status == ''
