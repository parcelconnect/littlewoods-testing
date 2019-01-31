import logging
from urllib.parse import parse_qs, urlencode, urljoin, urlparse

import requests

from .const import TRACKING_EVENT_STATUS
from .exceptions import FastwayAPIError, LabelNotFound, ValidationError

logger = logging.getLogger(__name__)


class Client:
    """Client for Fastway's API v2

    Docs: http://ie.api.fastway.org/v2/docs
    """

    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def _make_url(self, url, params=None):
        base_url = urljoin(self.base_url, '/v2/')
        url = urljoin(base_url, url)

        if params is None:
            params = {}
        params['api_key'] = self.api_key
        return self._update_query(url, **params)

    def _update_query(self, url, **kwargs):
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        query.update(kwargs)
        qs = urlencode(query, True)
        return parsed._replace(query=qs).geturl()

    def _request(self, method, url, params=None, **kwargs):
        """Wrapper around requests.request()

        - Adds api_key to query arguments in the URL
        - Handles errors, generating a specific exception

        Args:
            method: HTTP method to use
            url: path, relative to BASE_URL
            params: query string parameters
            json: json data to be sent to server
            **kwargs: passed directly to ``.request()``

        Returns:
            requests.Response: HTTP response

        Raises:
            FastwayAPIError: on connection failure, or non-2xx
                response status

        """
        url = self._make_url(url, params=params)
        log_safe_url = self._update_query(url, api_key='APIKEY-HIDDEN')

        logger.info('Fastway Client: %s %s', method.upper(), log_safe_url)

        try:
            response = requests.request(method, url, **kwargs)
        except requests.exceptions.RequestException as e:
            msg = 'Error connecting to the Fastway API: %s'
            args = (repr(e),)
            logger.warning(msg, *args, exc_info=True)
            raise FastwayAPIError(msg % args)

        if not response.ok:
            self._handle_http_error(response)

        return response

    def _handle_http_error(self, response):
        message = 'HTTP error %(code)s: %(message)s'
        error_msg = self._get_error_message(response)
        args = dict(code=response.status_code, message=error_msg)

        logger.warning(message, args, extra={'response': response.content})
        raise FastwayAPIError(message % args)

    def _get_error_message(self, response):
        return str(response.content)

    def _request_json(self, method, url, **kwargs):
        response = self._request(method, url, **kwargs)
        data = response.json()

        if 'error' in data:
            logger.info(
                'Fastway API returned an error: %s', data['error'],
                extra={
                    'method': method,
                    'url': url,
                    'response_json': data
                }
            )
            raise FastwayAPIError(data['error'])

        return data

    def _get_json(self, url, **kwargs):
        return self._request_json('GET', url, **kwargs)

    def _translate_status(self, code):
        try:
            return TRACKING_EVENT_STATUS[code]
        except KeyError:
            logger.error('Unknown status type "{}"'.format(code))
            return ''

    def get_tracking_events(self, label_id):
        """Returns tracking events for the given label.

        :param label_id: label id, 12 characters long

        http://ie.api.fastway.org/v2/docs/detail?ControllerName=tracktrace&
            ActionName=detail&api_key=

        """
        try:
            response = self._get_json('tracktrace/detail/{}'.format(label_id))
        except FastwayAPIError as e:
            if 'Label' in str(e) and 'does not have any scans' in str(e):
                if label_id.startswith('JJD'):
                    # Drop extra J and retry
                    try:
                        return self.get_tracking_events(label_id[1:])
                    except (FastwayAPIError, LabelNotFound):
                        # Use previous information for the error
                        pass
                raise LabelNotFound(
                    'No tracking information found for {}.<br />This means '
                    'your order has not yet been processed and shipped.'
                    .format(label_id))
            elif 'Invalid label number' in str(e):
                raise ValidationError('Invalid label ID')
            else:
                raise
        data = []
        for event in response['result']['Scans']:
            event['TypeVerbose'] = self._translate_status(event['Type'])
            data.append(event)
        return data
