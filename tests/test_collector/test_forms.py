import datetime

import pytest
from freezegun import freeze_time

from idv.collector.forms import AccountForm


class TestAccountForm:

    def test_does_not_validate_incorrent_email(self):
        form = AccountForm({
            'email': 'oops',
            'account_number': '12341234'
        })
        assert form.is_valid() is False
        assert 'email' in form.errors

    def test_invalid_account_number_length(self):
        form = AccountForm({
            'email': 'oops.I.did@it.again',
            'account_number': '1234123412'
        })
        assert form.is_valid() is False
        assert 'account_number' in form.errors

    def test_invalid_account_number_characters(self):
        form = AccountForm({
            'email': 'oops.I.did@it.again',
            'account_number': '123$123a'
        })
        assert form.is_valid() is False
        assert 'account_number' in form.errors

    @freeze_time('2019-01-01 00:00')
    def test_invalid_dates_are_in_the_future(self):
        form = AccountForm({
            'email': 'oops.I.did@it.again',
            'account_number': '12ca1234',
            'date_1': datetime.date(2019, 1, 2),
            'date_2': datetime.date(2019, 1, 3),
        })
        assert form.is_valid() is False
        assert form.errors['date_1'][0] == 'The date is in the future.'
        assert form.errors['date_2'][0] == 'The date is in the future.'

    def test_invalid_dates_format(self):
        form = AccountForm({
            'email': 'oops.I.did@it.again',
            'account_number': '12ca1234',
            'date_1': 'this is not a date',
            'date_2': 'this is not a date',
        })
        assert form.is_valid() is False
        assert form.errors['date_1'][0] == 'Enter a valid date.'
        assert form.errors['date_2'][0] == 'Enter a valid date.'

    @freeze_time('2019-02-01 00:00')
    @pytest.mark.parametrize('date_1,date_2', [
        (datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)),  # both in past
        (datetime.date(2019, 2, 1), datetime.date(2019, 2, 1)),  # both today
    ])
    def test_validates_correct_full_data(self, date_1, date_2):
        form = AccountForm({
            'email': 'oops.I.did@it.again',
            'account_number': '12ca1234',
            'date_1': date_1,
            'date_2': date_2,
        })
        assert form.is_valid() is True

    def test_validates_correct_data_without_dates(self):
        form = AccountForm({
            'email': 'oops.I.did@it.again',
            'account_number': '12ca1234',
        })
        assert form.is_valid() is True
