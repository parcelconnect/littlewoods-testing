import mock

import pytest
from freezegun import freeze_time

from idv.collector import domain as collector_domain
from idv.mover.commands import move
from idv.mover.domain import (
    get_last_move_checkpoint, has_whitelisted_extension)


@pytest.mark.django_db
class TestWhitelistedExceptions:

    def test_whitelisted_weirdcase_extension(self, account):
        cred = collector_domain.create_credential(account, 'photo.jPeG')
        assert has_whitelisted_extension(cred) is True

    def test_fails_on_unknown_extension(self, account):
        cred = collector_domain.create_credential(account, 'photo.xcv.exE')
        assert has_whitelisted_extension(cred) is False

    def test_fails_if_no_extension(self, account):
        cred = collector_domain.create_credential(account, 'photasdf')
        assert has_whitelisted_extension(cred) is False


@pytest.mark.django_db
class TestMoveCheckpoint:

    def test_returns_none_if_no_checkpoint(self):
        assert get_last_move_checkpoint() is None

    @freeze_time('2016-02-01 01:02:03')
    @mock.patch('idv.mover.commands.move_credential_files')
    def test_returns_checkpoint(self, move_creds_mock):
        move()
        checkpoint = get_last_move_checkpoint()
        assert checkpoint.year == 2016
        assert checkpoint.month == 2
        assert checkpoint.day == 1
        assert checkpoint.hour == 1
        assert checkpoint.minute == 2
        assert checkpoint.second == 3
