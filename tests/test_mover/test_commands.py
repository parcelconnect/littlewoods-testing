from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time
from unittest.mock import patch

from django.utils import timezone

from idv.collector import domain as collector_domain
from idv.collector.models import Credential
from idv.mover.commands import move, send_move_report
from idv.mover.domain import get_last_move_checkpoint


@pytest.mark.django_db
@freeze_time('2016-02-01 01:02:03')
class TestMove:

    @patch('idv.mover.commands.move_credential_files')
    def test_logs_start_of_successful_move(self, move_creds_mock):
        move()
        checkpoint = get_last_move_checkpoint()
        assert checkpoint.year == 2016
        assert checkpoint.month == 2
        assert checkpoint.day == 1
        assert checkpoint.hour == 1
        assert checkpoint.minute == 2
        assert checkpoint.second == 3

    @patch('idv.mover.commands.move_credential_files')
    def test_does_not_log_start_of_failed_move(self, move_creds_mock):
        move_creds_mock.side_effect = ValueError()
        with pytest.raises(ValueError):
            move()
        assert get_last_move_checkpoint() is None

    @patch('idv.mover.commands.move_credential_files', autospec=True)
    def test_filters_credentials_by_creation_date(self, move_creds_mock,
                                                  account):
        with freeze_time('2016-01-01'):
            cred1 = collector_domain.create_credential(account, 'zxcv.jpg')
            cred1.mark_as_found()
        with freeze_time('2016-02-01'):
            cred2 = collector_domain.create_credential(account, 'zxcv.jpg')
            cred2.mark_as_found()
        with freeze_time('2016-02-01'):
            move()

        args, kwargs = move_creds_mock.call_args
        assert move_creds_mock.call_count == 1
        assert len(args) == 1
        assert len(args[0]) == 1
        assert args[0][0] == cred1

    @patch('idv.mover.commands.move_credential_files')
    def test_moves_only_credentials_need_moving(self, move_creds_mock,
                                                credentials, account):
        with freeze_time('2016-01-05'):
            found2 = collector_domain.create_credential(account, 'zxcv.jpg')
            found2.mark_as_found()
        need_moving = Credential.objects.need_moving()
        move()

        args, kwargs = move_creds_mock.call_args
        assert len(args[0]) == 4
        assert need_moving[0] in args[0]
        assert need_moving[1] in args[0]
        assert need_moving[2] in args[0]
        assert need_moving[3] in args[0]


@pytest.mark.django_db
class TestSendMoreReport:

    def test_value_error_if_no_move_checkpoint(self):
        since = timezone.now().date()
        until = since + timedelta(days=1)
        with pytest.raises(ValueError):
            send_move_report(since, until)

    @patch('idv.mover.commands.move_credential_files')
    def test_value_error_if_checkpoint_older_than_report_end_date(self, m):
        with freeze_time('2016-01-05'):
            move()

        since = datetime(2016, 1, 4).date()
        until = datetime(2016, 1, 6).date()
        with pytest.raises(ValueError):
            send_move_report(since, until)

    @patch('idv.mover.commands.mover_mail')
    @patch('idv.mover.commands.move_credential_files')
    def test_report_sending(self, move_mock, mail_mock):
        with freeze_time('2016-01-05'):
            move()

        since = datetime(2016, 1, 4).date()
        until = datetime(2016, 1, 5).date()
        send_move_report(since, until)
        mail_mock.send_move_report.assert_called_once_with((since, until))
