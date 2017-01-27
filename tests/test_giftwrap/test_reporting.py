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

    @patch('idv.giftwrap.reporting.create_mail')
    def test_it_sends_email_with_upis_when_found_for_given_day(
            self, mock_create_mail, settings, request_success):
        settings.UPI_REPORT_RECIPIENTS = ["example@example.com"]
        run_report_at = request_success.created_at.date()
        formatted_date = run_report_at.strftime("%dth of %B")
        subject = ('Littlewoods ID&V Gift Wrapping Requests processed '
                   'on the {}'.format(formatted_date))
        message = ('There were 1 successful gift wrapping requests processed '
                   'on the {}.\n{}\n'
                   .format(formatted_date, request_success.upi))
        send_report_email(run_report_at)
        mock_create_mail.assert_called_once_with(
            subject=subject,
            context=message,
            emails=["example@example.com"]
        )

    @patch('idv.giftwrap.reporting.create_mail')
    def test_it_sends_email_when_no_upis_found_for_given_day(
            self, mock_create_mail, settings):
        settings.UPI_REPORT_RECIPIENTS = ["example@example.com"]
        run_report_at = datetime.now().date()
        formatted_date = run_report_at.strftime("%dth of %B")
        subject = ('Littlewoods ID&V Gift Wrapping Requests processed '
                   'on the {}'.format(formatted_date))
        message = ('There were 0 successful gift wrapping requests processed '
                   'on the {}.\n'
                   .format(formatted_date))
        send_report_email(run_report_at)
        mock_create_mail.assert_called_once_with(
            subject=subject,
            context=message,
            emails=["example@example.com"]
        )
