import pytest

from idv.tracker.est_delivery_date import get_est_delivery_date_from_event


@pytest.fixture
def hdn_scan_event():
    return {
        'status_scan': 'HDN',
        'date': 'April 6, 2018'}


@pytest.fixture
def r10_scan_event_day_before_bank_holiday():
    return {
        'status_scan': 'R10',
        'date': 'April 1, 2018'}


@pytest.fixture
def ds1_scan_event_on_friday():
    return {
        'status_scan': 'R10',
        'date': 'April 6, 2018'}


def test_returns_correct_date(hdn_scan_event):
    est_delivery_date = get_est_delivery_date_from_event(hdn_scan_event)
    assert est_delivery_date == hdn_scan_event['date']


def test_returns_correct_date_when_end_date_during_bank_holiday(
        r10_scan_event_day_before_bank_holiday):
    est_delivery_date = get_est_delivery_date_from_event(
            r10_scan_event_day_before_bank_holiday)
    assert est_delivery_date == 'April 03, 2018'


def test_returns_correct_date_when_end_date_during_weekend(
        ds1_scan_event_on_friday):
    est_delivery_date = get_est_delivery_date_from_event(
            ds1_scan_event_on_friday)
    assert est_delivery_date == 'April 09, 2018'
