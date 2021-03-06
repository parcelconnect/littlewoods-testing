from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from freezegun import freeze_time

from idv.giftwrap.reporting import (
    FROM_DATE, _get_success_upis_for_day, send_report_email)


@pytest.mark.django_db
class TestGetSuccessfulUpis:

    def test_it_returns_upis_when_found_on_given_day(
            self, request_success):
        run_report_at = request_success.created_at.date()
        successful_upis = _get_success_upis_for_day(run_report_at)
        assert len(successful_upis) == 1

    def test_it_does_not_return_upi_when_different_day_given(
            self, request_success):
        run_report_at = request_success.created_at.date() - timedelta(days=1)
        successful_upis = _get_success_upis_for_day(run_report_at)
        assert len(successful_upis) == 0


@pytest.mark.django_db
class TestSendReportEmail:

    def test_from_date_is_timezone_aware(self):
        assert FROM_DATE.tzinfo is not None
        assert FROM_DATE.tzinfo.utcoffset(FROM_DATE) is not None

    @freeze_time('2017-05-02')
    @patch('idv.giftwrap.reporting.EmailMultiAlternatives')
    def test_it_sends_email_with_upis_when_found_for_given_day(
            self, mock_EmailMultiAlternatives, settings, request_success):
        settings.UPI_REPORT_RECIPIENTS = ["example@example.com"]
        request_success.created_at = timezone.now()
        request_success.save()
        run_report_at = request_success.created_at.date()
        formatted_date = run_report_at.strftime("%B %d")
        subject = ('Littlewood\'s Gift Wrapping Requests processed '
                   'on {}'.format(formatted_date))
        message = (
            'There were 1 gift wrapping requests processed on '
            '2017-05-02.\r\nAAAAAAAAAAAAA\r\n'
            '\r\n\r\nThere were 1 gift '
            'wrapping requests processed until 2017-05-02.\r\nAAAAAAAAAAAAA'
            '\r\n\r\n\r\n'
            'There were 1 customer gift wrapping requests on 2017-05-02.\r\n'
            '\r\n\r\n'
            'There were 1 customer gift wrapping requests made'
            ' until 2017-05-02.\r\n'
        )
        from_email = 'support@fastway.ie'
        send_report_email(run_report_at)
        mock_EmailMultiAlternatives.assert_called_once_with(
            subject,
            message,
            from_email,
            ["example@example.com"]
        )

    @freeze_time('2017-02-21')
    @patch('idv.giftwrap.reporting.EmailMultiAlternatives')
    def test_it_sends_email_when_no_upis_found_for_given_day(
            self, mock_EmailMultiAlternatives, settings):
        settings.UPI_REPORT_RECIPIENTS = ["example@example.com"]
        run_report_at = timezone.now().date()
        formatted_date = run_report_at.strftime("%B %d")
        subject = ('Littlewood\'s Gift Wrapping Requests processed '
                   'on {}'.format(formatted_date))
        message = (
            'There were 0 gift wrapping requests processed on '
            '2017-02-21.\r\n'
            '\r\n\r\nThere were 0 gift wrapping requests processed'
            ' until 2017-02-21.\r\n'
            '\r\n\r\nThere were 0 customer gift wrapping requests on '
            '2017-02-21.\r\n'
            '\r\n\r\nThere were 0 customer gift wrapping requests made'
            ' until 2017-02-21.\r\n'
        )
        from_email = 'support@fastway.ie'
        send_report_email(run_report_at)
        mock_EmailMultiAlternatives.assert_called_once_with(
            subject,
            message,
            from_email,
            ["example@example.com"]
        )
