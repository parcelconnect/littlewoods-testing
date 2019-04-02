import datetime

import pytest

from idv.tracker.est_delivery_date import (
    PLUS_1_DAY_SCANS, PLUS_2_DAYS_SCANS, SAME_DAY_SCANS,
    get_est_delivery_date_from_event, get_recipient_data)


@pytest.fixture
def hdn_scan_event():
    return {
        'status_scan': 'HDN',
        'date': 'April 06, 2018'}


@pytest.fixture
def r10_scan_event_day_before_bank_holiday():
    return {
        'status_scan': 'R10',
        'date': 'April 01, 2018'}


@pytest.fixture
def ds1_scan_event_on_friday():
    return {
        'status_scan': 'R10',
        'date': 'April 6, 2018'}


@pytest.fixture
def r02_scan_event_day_before_bank_holiday():
    return {
        'status_scan': 'R02',
        'date': 'April 01, 2018'}


@pytest.fixture
def rtd_scan_event_on_friday():
    return {
        'status_scan': 'RTD',
        'date': 'April 6, 2018'}


@pytest.fixture
def other_scan_event_on_friday():
    return {
        'status_scan': 'PPP',
        'date': 'April 6, 2018'}


class TestGetEstimateDeliveryDate:

    def test_returns_correct_date(self, hdn_scan_event):
        est_delivery_date = get_est_delivery_date_from_event(hdn_scan_event)
        assert est_delivery_date.strftime(
            '%B %d, %Y') == hdn_scan_event['date']

    def test_returns_correct_date_when_end_date_during_bank_holiday_for_r10(
            self, r10_scan_event_day_before_bank_holiday):
        est_delivery_date = get_est_delivery_date_from_event(
            r10_scan_event_day_before_bank_holiday)
        assert est_delivery_date == datetime.datetime(2018, 4, 3, 0, 0)

    def test_returns_correct_date_when_end_date_during_weekend_for_ds1(
            self, ds1_scan_event_on_friday):
        est_delivery_date = get_est_delivery_date_from_event(
            ds1_scan_event_on_friday)
        assert est_delivery_date == datetime.datetime(2018, 4, 9, 0, 0)

    def test_returns_correct_date_when_end_date_during_weekend_and_before_bank_holiday(  # noqa
            self, ds1_scan_event_on_friday):
        ds1_scan_event_on_friday['date'] = 'October 26, 2018'
        est_delivery_date = get_est_delivery_date_from_event(
            ds1_scan_event_on_friday)
        assert est_delivery_date == datetime.datetime(2018, 10, 30, 0, 0)

    def test_returns_correct_date_when_end_date_during_bank_holiday_for_r02(
            self, r02_scan_event_day_before_bank_holiday):
        est_delivery_date = get_est_delivery_date_from_event(
            r02_scan_event_day_before_bank_holiday)
        assert est_delivery_date == datetime.datetime(2018, 4, 3, 0, 0)

    def test_returns_correct_date_when_end_date_during_weekend_for_rtd(
            self, rtd_scan_event_on_friday):
        est_delivery_date = get_est_delivery_date_from_event(
            rtd_scan_event_on_friday)
        assert est_delivery_date == datetime.datetime(2018, 4, 9, 0, 0)

    def test_returns_correct_date_when_end_date_during_weekend_for_other(
            self, other_scan_event_on_friday):
        assert other_scan_event_on_friday['status_scan'] not in set(
            PLUS_1_DAY_SCANS + PLUS_2_DAYS_SCANS + SAME_DAY_SCANS)
        est_delivery_date = get_est_delivery_date_from_event(
            other_scan_event_on_friday)
        assert est_delivery_date == datetime.datetime(2018, 4, 9, 0, 0)


class TestGetRecipientData:

    def test_no_events(self):
        assert {} == get_recipient_data([])

    def test_if_address_not_empty_then_recipient_copied(self):
        events = [
            {
                'recipient': {
                    'address1': '',
                    'address2': '',
                    'contactName': '',
                }
            },
            {
                'recipient': {
                    'address1': 'Address',
                    'address2': '-',
                    'address3': '',
                    'contactName': '',
                }
            },
            {
                'recipient': {
                    'address1': '',
                    'address2': '',
                    'contactName': '',
                }
            },
        ]
        recipient = get_recipient_data(events)
        assert events[1]['recipient'] == recipient

    def test_if_contact_name_not_empty_then_copied(self):
        events = [
            {
                'recipient': {
                    'address1': '',
                    'address2': '',
                    'contactName': '',
                }
            },
            {
                'recipient': {
                    'address1': 'Address',
                    'address2': '-',
                    'address3': '',
                    'contactName': '',
                }
            },
            {
                'recipient': {
                    'address1': '',
                    'address2': '',
                    'contactName': 'Sławek',
                }
            },
        ]
        recipient = get_recipient_data(events)
        assert events[1]['recipient']['address1'] == recipient['address1']
        assert events[1]['recipient']['address2'] == recipient['address2']
        assert events[1]['recipient']['address3'] == recipient['address3']
        assert events[2]['recipient']['contactName'] == recipient['contactName']  # noqa
