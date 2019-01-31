import pytest
import vcr
from django.shortcuts import reverse

DEFAULT_MATCH_ON = ['method', 'scheme', 'host', 'port', 'path', 'query']
MATCH_ON = DEFAULT_MATCH_ON + ['body']


class TestGetTrackingEvents:

    @pytest.fixture(autouse=True)
    def client_settings(self, settings):
        settings.FASTWAY_API_KEY = 'APIKEY'
        settings.FASTWAY_API_ENDPOINT = 'http://ie.preview.api.fastway.org'

    @vcr.use_cassette('tests/test_tracker/cassettes/get_tracking_events.yml',
                      match_on=MATCH_ON)
    def test_returns_expected_data_populated_in_the_template(self, client):
        label_id = '9009298467801'
        url = reverse('tracker:get-events') + '?label_id={}'.format(label_id)

        response = client.get(url)

        content = response.content.decode()
        expected_context = {
            'label_id': '9009298467801',
            'events': [
                {
                    'status_scan': 'R02',
                    'status_description': 'Received in Hub - Portarlington Co Laois',  # noqa
                    'name': 'Hawkes Bay Couriers (Hub)',
                    'franchisee': 'HBC',
                    'date': 'March 12, 2018',
                    'description': 'Delivery Received in Hub',
                    'time': 'Monday, 07:17 AM',
                    'recipient': {
                        'comment': '',
                        'address1': '4 Dunsink Avenue',
                        'address8': '',
                        'company': 'MISS A DE-PREE',
                        'address4': 'Dublin 11',
                        'contactName': '',
                        'address2': 'Finglas West',
                        'address5': 'DB99 9AA',
                        'address3': 'Dublin',
                        'address6': '',
                        'address7': ''
                    }
                },
                {
                    'status_scan': 'R10',
                    'status_description': 'Received in DEPOT - Dublin',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 12, 2018',
                    'description': 'Recvd in Depot:Inbound Freight',
                    'time': 'Monday, 10:25 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '',
                       'address8': '',
                       'company': '',
                       'address4': '',
                       'contactName': '',
                       'address2': '',
                       'address5': '',
                       'address3': '',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'U38',
                    'status_description': 'Transit',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 13, 2018',
                    'description': 'Delivery on Future Date',
                    'time': 'Tuesday, 12:38 PM',
                    'recipient': {
                       'comment': '',
                       'address1': '',
                       'address8': '',
                       'company': '',
                       'address4': '',
                       'contactName': '',
                       'address2': '',
                       'address5': '',
                       'address3': '',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'U38',
                    'status_description': 'Transit',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 14, 2018',
                    'description': 'Delivery on Future Date',
                    'time': 'Wednesday, 11:57 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '',
                       'address8': '',
                       'company': '',
                       'address4': '',
                       'contactName': '',
                       'address2': '',
                       'address5': '',
                       'address3': '',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'U38',
                    'status_description': 'Transit',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 15, 2018',
                    'description': 'Delivery on Future Date',
                    'time': 'Thursday, 11:30 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '',
                       'address8': '',
                       'company': '',
                       'address4': '',
                       'contactName': '',
                       'address2': '',
                       'address5': '',
                       'address3': '',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'ONB',
                    'status_description': 'On Board with courier',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 16, 2018',
                    'description': 'On Board with Courier',
                    'time': 'Friday, 07:12 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '4 Dunsink Avenue',
                       'address8': '',
                       'company': 'MISS A DE-PREE',
                       'address4': 'IRELAND',
                       'contactName': 'MISS A DE-PREE',
                       'address2': 'Finglas West',
                       'address5': 'DB99 9AA',
                       'address3': 'Dublin 11',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'HDN',
                    'status_description': 'Delivery',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 16, 2018',
                    'description': 'ATL Safe Delivery Location',
                    'time': 'Friday, 10:21 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '4 Dunsink Avenue',
                       'address8': '',
                       'company': 'MISS A DE-PREE',
                       'address4': 'IRELAND',
                       'contactName': 'MISS A DE-PREE',
                       'address2': 'Finglas West',
                       'address5': 'DB99 9AA',
                       'address3': 'Dublin 11',
                       'address6': '',
                       'address7': ''
                    }
                }
            ],
            'recipient_data': {
                'comment': '',
                 'address1': '4 Dunsink Avenue',
                 'address8': '',
                 'company': 'MISS A DE-PREE',
                 'address4': 'IRELAND',
                 'contactName': 'MISS A DE-PREE',
                 'address2': 'Finglas West',
                 'address5': 'DB99 9AA',
                 'address3': 'Dublin 11',
                 'address6': '',
                 'address7': ''
            },
            'success': True,
            'est_delivery_month': 'March 2018',
            'est_delivery_day_str': 'Friday',
            'est_delivery_day': '16'
        }

        assert response.status_code == 200
        assert 'Customer:' not in content
        assert 'Arriving:' in content
        assert 'Delivery Address:' in content
        assert '4 Dunsink Avenue' in content
        assert 'Dublin 11' in content
        assert 'IRELAND' in content
        assert 'DB99 9AA' in content
        assert 'Received in Hub - Portarlington Co Laois' in content
        assert 'Received in DEPOT - Dublin' in content
        assert 'Transit' in content
        assert 'On Board with courier' in content
        assert 'Delivery' in content
        for key in expected_context.keys():
            assert expected_context[key] == response.context[key]

    @vcr.use_cassette('tests/test_tracker/cassettes/get_tracking_events.yml',
                      match_on=MATCH_ON)
    def test_returns_expected_data_populated_in_the_template_for_jjd_label(
            self, client):
        label_id = 'JJD0000000000000001'
        url = reverse('tracker:get-events') + '?label_id={}'.format(label_id)

        response = client.get(url)

        content = response.content.decode()
        expected_context = {
            'label_id': 'JJD0000000000000001',
            'events': [
                {
                    'status_scan': 'R02',
                    'status_description': 'Received in Hub - Portarlington Co Laois',  # noqa
                    'name': 'Hawkes Bay Couriers (Hub)',
                    'franchisee': 'HBC',
                    'date': 'March 12, 2018',
                    'description': 'Delivery Received in Hub',
                    'time': 'Monday, 07:17 AM',
                    'recipient': {
                        'comment': '',
                        'address1': '4 Dunsink Avenue',
                        'address8': '',
                        'company': 'MISS A DE-PREE',
                        'address4': 'Dublin 11',
                        'contactName': '',
                        'address2': 'Finglas West',
                        'address5': 'DB99 9AA',
                        'address3': 'Dublin',
                        'address6': '',
                        'address7': ''
                    }
                },
                {
                    'status_scan': 'R10',
                    'status_description': 'Received in DEPOT - Dublin',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 12, 2018',
                    'description': 'Recvd in Depot:Inbound Freight',
                    'time': 'Monday, 10:25 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '',
                       'address8': '',
                       'company': '',
                       'address4': '',
                       'contactName': '',
                       'address2': '',
                       'address5': '',
                       'address3': '',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'U38',
                    'status_description': 'Transit',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 13, 2018',
                    'description': 'Delivery on Future Date',
                    'time': 'Tuesday, 12:38 PM',
                    'recipient': {
                       'comment': '',
                       'address1': '',
                       'address8': '',
                       'company': '',
                       'address4': '',
                       'contactName': '',
                       'address2': '',
                       'address5': '',
                       'address3': '',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'U38',
                    'status_description': 'Transit',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 14, 2018',
                    'description': 'Delivery on Future Date',
                    'time': 'Wednesday, 11:57 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '',
                       'address8': '',
                       'company': '',
                       'address4': '',
                       'contactName': '',
                       'address2': '',
                       'address5': '',
                       'address3': '',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'U38',
                    'status_description': 'Transit',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 15, 2018',
                    'description': 'Delivery on Future Date',
                    'time': 'Thursday, 11:30 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '',
                       'address8': '',
                       'company': '',
                       'address4': '',
                       'contactName': '',
                       'address2': '',
                       'address5': '',
                       'address3': '',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'ONB',
                    'status_description': 'On Board with courier',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 16, 2018',
                    'description': 'On Board with Courier',
                    'time': 'Friday, 07:12 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '4 Dunsink Avenue',
                       'address8': '',
                       'company': 'MISS A DE-PREE',
                       'address4': 'IRELAND',
                       'contactName': 'MISS A DE-PREE',
                       'address2': 'Finglas West',
                       'address5': 'DB99 9AA',
                       'address3': 'Dublin 11',
                       'address6': '',
                       'address7': ''
                    }
                },
                {
                    'status_scan': 'HDN',
                    'status_description': 'Delivery',
                    'name': 'Dublin',
                    'franchisee': 'DUB',
                    'date': 'March 16, 2018',
                    'description': 'ATL Safe Delivery Location',
                    'time': 'Friday, 10:21 AM',
                    'recipient': {
                       'comment': '',
                       'address1': '4 Dunsink Avenue',
                       'address8': '',
                       'company': 'MISS A DE-PREE',
                       'address4': 'IRELAND',
                       'contactName': 'MISS A DE-PREE',
                       'address2': 'Finglas West',
                       'address5': 'DB99 9AA',
                       'address3': 'Dublin 11',
                       'address6': '',
                       'address7': ''
                    }
                }
            ],
            'recipient_data': {
                'comment': '',
                 'address1': '4 Dunsink Avenue',
                 'address8': '',
                 'company': 'MISS A DE-PREE',
                 'address4': 'IRELAND',
                 'contactName': 'MISS A DE-PREE',
                 'address2': 'Finglas West',
                 'address5': 'DB99 9AA',
                 'address3': 'Dublin 11',
                 'address6': '',
                 'address7': ''
            },
            'success': True,
            'est_delivery_month': 'March 2018',
            'est_delivery_day_str': 'Friday',
            'est_delivery_day': '16'
        }

        assert response.status_code == 200
        assert 'Customer:' not in content
        assert 'Arriving:' in content
        assert 'Delivery Address:' in content
        assert '4 Dunsink Avenue' in content
        assert 'Dublin 11' in content
        assert 'IRELAND' in content
        assert 'DB99 9AA' in content
        assert 'Received in Hub - Portarlington Co Laois' in content
        assert 'Received in DEPOT - Dublin' in content
        assert 'Transit' in content
        assert 'On Board with courier' in content
        assert 'Delivery' in content
        for key in expected_context.keys():
            assert expected_context[key] == response.context[key]

    @vcr.use_cassette('tests/test_tracker/cassettes/get_tracking_events.yml',
                      match_on=MATCH_ON)
    def test_returns_400_when_label_id_is_invalid(self, client):
        label_id = 'NON-EXISTING'
        url = reverse('tracker:get-events') + '?label_id={}'.format(label_id)

        response = client.get(url)

        assert response.status_code == 400
        assert response.json() == {
            'message': 'Invalid label ID', 'success': False}

    @vcr.use_cassette('tests/test_tracker/cassettes/get_tracking_events.yml',
                      match_on=MATCH_ON)
    def test_returns_400_when_jjd_label_id_is_invalid(self, client):
        label_id = 'JJD0000000000000002'
        url = reverse('tracker:get-events') + '?label_id={}'.format(label_id)

        response = client.get(url)

        assert response.status_code == 400
        assert response.json() == {
            'message': 'No tracking information found for JJD0000000000000002.'
                       '<br />This means your order has not yet been '
                       'processed and shipped.',
            'success': False}

    @vcr.use_cassette('tests/test_tracker/cassettes/get_tracking_events.yml',
                      match_on=MATCH_ON)
    def test_returns_400_when_label_id_has_no_tracking_details(
            self, client):
        label_id = '9009298467800'
        url = reverse('tracker:get-events') + '?label_id={}'.format(label_id)

        response = client.get(url)

        assert response.status_code == 400
        assert response.json() == {
            'message': 'No tracking information found for 9009298467800.<br />'
                       'This means your order has not yet been processed and '
                       'shipped.',
            'success': False}
