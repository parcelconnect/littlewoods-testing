from datetime import timedelta
from unittest.mock import call, patch

from django.core.management import call_command
from django.utils import timezone


class TestSendUpiReport:

    @patch('idv.giftwrap.management.commands.send_upi_report.send_report_email')  # noqa
    def test_invokes_send_report_email_with_expected_parameter(
            self, mock_method):
        expected_date = timezone.now().date() - timedelta(days=1)

        call_command('send_upi_report')

        assert mock_method.call_count == 1
        assert mock_method.call_args == call(expected_date)
