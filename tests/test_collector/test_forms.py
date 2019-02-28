import datetime

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

    def test_invalid_dates(self):
        form = AccountForm({
            'email': 'oops.I.did@it.again',
            'account_number': '12ca1234',
            'date_1': 'this is not a date',
            'date_2': 'this is not a date',
        })
        assert form.is_valid() is False
        assert 'date_1' in form.errors
        assert 'date_2' in form.errors

    def test_validates_correct_data(self):
        form = AccountForm({
            'email': 'oops.I.did@it.again',
            'account_number': '12ca1234',
            'date_1': datetime.date(2019, 1, 1),
            'date_2': datetime.date(2019, 1, 2),
        })
        assert form.is_valid() is True
