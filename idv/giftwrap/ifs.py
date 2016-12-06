import logging
from urllib.parse import urljoin

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class IFSAPIError(Exception):
    pass


class TooLateError(Exception):
    pass


class Client:
    """Client for the IFS API."""
    GIFTWRAP_URL_PATH = "/webhooks/giftwrap/"
    REFERER = "Littlewoods"
    USER_AGENT = "Littlewoods Gift Wrapping"

    def __init__(self, base_url, username, password, test_mode=False):
        self.base_url = base_url
        self.username = username
        self.password = password

        self._session = self.create_session(username, password)

    @classmethod
    def create_session(cls, username, password):
        session = requests.Session()
        session.auth = (username, password)
        session.headers.update({
            'User-Agent': cls.USER_AGENT,
            'referer': cls.REFERER
        })
        return session

    def _post(self, path, data):
        url = urljoin(self.base_url, path)
        logger.info('[IFS]: POST Request to %s: %s', url, data)

        try:
            resp = self._session.post(url, json=data)
        except requests.exceptions.RequestException as e:
            raise IFSAPIError(
                'Error connecting to the IFS API: %s'.format(e)) from e

        logger.info('[IFS]: POST Response (%s) from %s: %s', resp.status_code,
                    url, resp.content.decode())
        return resp

    def request_gift_wrap(self, upi, address=None):
        data = {
            "giftwrap": {
                "mode": "test",
                "upi": [upi],
            }
        }
        if address:
            data['giftwrap']['receiver'] = {
                "add1": address['address'],
                "contact": address['name'],
                "phone": address['phone_number']
            }
        response = self._post(self.GIFTWRAP_URL_PATH, data)

        if response.status_code != 200:
            raise IFSAPIError('Got {} status code'.
                              format(response.status_code))
        elif response.status_code == 200:
            status = response.json().get('status')
            if status == "fail":
                raise TooLateError('Too late to gift wrap UPI {}'.format(upi))
            elif status != "ok":
                raise IFSAPIError('Unkown response status. Response: {}'
                                  .format(response.json()))
        return True


def get_client_from_settings():
    required_vars = [
        'IFS_API_ENDPOINT', 'IFS_API_USERNAME', 'IFS_API_PASSWORD']
    for var in required_vars:
        if not getattr(settings, var):
            raise ValueError('Cannot create IFS client from settings. '
                             '{} is not set.'.format(var))
    return Client(
        base_url=settings.IFS_API_ENDPOINT,
        username=settings.IFS_API_USERNAME,
        password=settings.IFS_API_PASSWORD,
        test_mode=settings.IFS_API_TEST_MODE
    )
