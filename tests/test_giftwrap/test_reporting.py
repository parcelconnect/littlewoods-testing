from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from idv.giftwrap.reporting import (
    get_successful_upis_for_day, send_report_email
)


@pytest.mark.django_db
class TestGetSuccessfulUpis:

    def test_it_returns_upis_when_found_on_given_day(
            self, request_success):
        run_report_at = request_success.created_at.date()
        successful_upis = get_successful_upis_for_day(run_report_at)
        assert len(successful_upis) == 1

    def test_it_does_not_return_upi_when_different_day_given(
            self, request_success):
        run_report_at = request_success.created_at.date() - timedelta(days=1)
        successful_upis = get_successful_upis_for_day(run_report_at)
        assert len(successful_upis) == 0


@pytest.mark.django_db
class TestSendReportEmail:

    @patch('idv.giftwrap.reporting.EmailMultiAlternatives')
    def test_it_sends_email_with_upis_when_found_for_given_day(
            self, mock_EmailMultiAlternatives, settings, request_success):
        settings.UPI_REPORT_RECIPIENTS = ["example@example.com"]
        run_report_at = request_success.created_at.date()
        formatted_date = run_report_at.strftime("%B %d")
        subject = ('Littlewood\'s Gift Wrapping Requests processed '
                   'on {}'.format(formatted_date))
        message = ('There were 1 successful gift wrapping requests processed '
                   'on {}.\r\n{}\r\n'
                   .format(formatted_date, request_success.upi))
        from_email = 'support@fastway.ie'
        send_report_email(run_report_at)
        mock_EmailMultiAlternatives.assert_called_once_with(
            subject,
            message,
            from_email,
            ["example@example.com"]
        )

    @patch('idv.giftwrap.reporting.EmailMultiAlternatives')
    def test_it_sends_email_when_no_upis_found_for_given_day(
            self, mock_EmailMultiAlternatives, settings):
        settings.UPI_REPORT_RECIPIENTS = ["example@example.com"]
        run_report_at = datetime.now().date()
        formatted_date = run_report_at.strftime("%B %d")
        subject = ('Littlewood\'s Gift Wrapping Requests processed '
                   'on {}'.format(formatted_date))
        message = ('There were 0 successful gift wrapping requests processed '
                   'on {}.\r\n'
                   .format(formatted_date))
        from_email = 'support@fastway.ie'
        send_report_email(run_report_at)
        mock_EmailMultiAlternatives.assert_called_once_with(
            subject,
            message,
            from_email,
            ["example@example.com"]
        )
