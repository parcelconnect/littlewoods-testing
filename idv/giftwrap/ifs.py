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
    YODEL_TRAILING_ID = '049'

    def __init__(self, base_url, username, password, test_mode=False):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.test_mode = test_mode

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
            error_msg = '[IFS]: Request error: %s'
            logger.error(error_msg, e)
            raise IFSAPIError(error_msg % e) from e

        logger.info('[IFS]: POST Response (%s) from %s: %s', resp.status_code,
                    url, resp.content.decode())
        return resp

    def request_gift_wrap(self, upi, address=None):
        real_upi = upi + self.YODEL_TRAILING_ID
        data = {
            "giftwrap": {
                "upi": [real_upi],
            }
        }
        if self.test_mode is True:
            data["giftwrap"]["mode"] = "test"
        if address:
            data['giftwrap']['receiver'] = {
                "add1": address['address1'],
                "add2": address['address2'],
                "add3": address['town'],
                "add4": address['county'],
                "add5": "",
                "add6": "Ireland",  # Only Ireland is supported
                "contact": address['name'],
                "phone": address['phone_number']
            }
        response = self._post(self.GIFTWRAP_URL_PATH, data)

        if response.status_code != 200:
            error_msg = '[IFS]: Unexpected status status code %s'
            logger.error(error_msg, response.status_code)
            raise IFSAPIError(error_msg % response.status_code)
        elif response.status_code == 200:
            response_content = response.json()
            status = response_content.get('status')
            if status == "fail":
                raise TooLateError('Too late to gift wrap UPI {}'.format(upi))
            elif status != "ok":
                error_msg = '[IFS]: response status value not "ok": %s'
                logger.error(error_msg, status)
                raise IFSAPIError(error_msg % status)
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
