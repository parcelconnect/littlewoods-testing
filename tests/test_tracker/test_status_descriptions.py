import pytest

from idv.tracker.status_descriptions import map_status_to_description


@pytest.fixture
def fastway_onb_scan_event():
    return {'Status': 'ONB', 'TypeVerbose': 'In Transit'}


@pytest.fixture
def fastway_r09_scan_event():
    return {'Status': 'R09', 'TypeVerbose': 'In Transit'}


def test_returns_status_description(fastway_onb_scan_event):
    assert map_status_to_description(
        fastway_onb_scan_event) == 'On Board with courier'


def test_returns_event_type_if_no_description_found(fastway_r09_scan_event):
    assert map_status_to_description(
        fastway_r09_scan_event) == 'In Transit'
