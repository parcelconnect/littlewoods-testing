from argparse import ArgumentTypeError
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone
from freezegun import freeze_time

from idv.collector import domain as collector_domain
from idv.collector.models import Credential
from idv.mover.commands import move
from idv.mover.domain import get_last_move_checkpoint
from idv.mover.management.commands.send_report import valid_date
from idv.mover.tasks import send_move_report
from tests.conftest import wait_for_ping


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
            cred1 = collector_domain.create_credential(account, 'zxcv.jpg',
                                                       'normal')
            cred1.mark_as_found()
        with freeze_time('2016-02-01'):
            cred2 = collector_domain.create_credential(account, 'zxcv.jpg',
                                                       'normal')
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
            found2 = collector_domain.create_credential(account, 'zxcv.jpg',
                                                        'normal')
            found2.mark_as_found()
        need_moving = Credential.objects.need_moving()

        call_command('move')

        args, kwargs = move_creds_mock.call_args
        assert len(args[0]) == 4
        assert need_moving[0] in args[0]
        assert need_moving[1] in args[0]
        assert need_moving[2] in args[0]
        assert need_moving[3] in args[0]


@pytest.mark.django_db(transaction=True)
class TestSendReport:

    @pytest.fixture(autouse=True)
    def use_celery_worker(self, celery_worker):
        pass

    @pytest.mark.parametrize('arg_date,expected_date',
                             [('2018-01-31', datetime(2018, 1, 31).date()),
                              ('2016-02-29', datetime(2016, 2, 29).date()),
                              ('2019-04-01', datetime(2019, 4, 1).date())])
    def test_valid_date_returns_expected_date(self, arg_date, expected_date):
        assert valid_date(arg_date) == expected_date

    @pytest.mark.parametrize('arg_date',
                             ['Invalid', '2019-02-29', '01/01/2001'])
    def test_raises_exception_when_invalid_date(self, arg_date):
        with pytest.raises(ArgumentTypeError):
            valid_date(arg_date)

    @patch('idv.mover.tasks.mover_mail')
    @patch('idv.mover.commands.move_credential_files')
    @freeze_time('2016-01-05')
    def test_command_send_email_for_yesterday(self, move_mock, mail_mock):
        move()
        since = datetime(2016, 1, 4).date()
        until = datetime(2016, 1, 5).date()
        call_command('send_report')

        wait_for_ping()

        mail_mock.send_move_report.assert_called_once_with((since, until))

    @patch('idv.mover.tasks.mover_mail')
    @patch('idv.mover.commands.move_credential_files')
    @freeze_time('2016-01-05')
    def test_command_send_email_for_given_dates(self, move_mock, mail_mock):
        move()
        since = datetime(2016, 1, 2).date()
        until = datetime(2016, 1, 3).date()
        call_command('send_report', since=since, until=until)

        wait_for_ping()

        mail_mock.send_move_report.assert_called_once_with((since, until))

    @patch('idv.mover.tasks.mover_mail')
    @patch('idv.mover.commands.move_credential_files')
    def test_value_error_if_no_move_checkpoint(self, move_mock, mail_mock):
        since = timezone.now().date()
        until = since + timedelta(days=1)

        call_command('send_report', since=since, until=until)
        wait_for_ping()

        assert not mail_mock.called

    @patch('idv.mover.tasks.mover_mail')
    @patch('idv.mover.commands.move_credential_files')
    def test_retries_if_checkpoint_older_than_report_end_date(
            self, move_mock, mail_mock):
        with freeze_time('2016-01-05'):
            move()

        since = datetime(2016, 1, 4).date()
        until = datetime(2016, 1, 6).date()

        call_command('send_report', since=since, until=until)
        wait_for_ping()

        assert not mail_mock.called

    @patch('idv.mover.tasks.mover_mail')
    @patch('idv.mover.commands.move_credential_files')
    def test_retries_if_move_didnt_finish_on_time(
            self, move_mock, mail_mock, settings):
        settings.SEND_REPORT_RETRY_TIME = 1

        with freeze_time('2016-01-05'):
            move()

        since = datetime(2016, 1, 4).date()
        until = datetime(2016, 1, 6).date()

        call_command('send_report', since=since, until=until)
        wait_for_ping()

        with freeze_time('2016-01-06'):
            move()

        wait_for_ping()
        mail_mock.send_move_report.assert_called_once_with((since, until))

    @patch('idv.mover.tasks.mover_mail')
    @patch('idv.mover.commands.move_credential_files')
    def test_report_sending(self, move_mock, mail_mock):
        with freeze_time('2016-01-05'):
            move()

        since = datetime(2016, 1, 4).date()
        until = datetime(2016, 1, 5).date()
        send_move_report("2016-01-04", "2016-01-05")
        mail_mock.send_move_report.assert_called_once_with((since, until))
