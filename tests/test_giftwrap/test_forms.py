from idv.giftwrap.forms import GiftWrapRequestForm


class TestGiftWrapRequestForm:

    def test_invalid_account_number_with_symbols(self):
        form = GiftWrapRequestForm(data={'account_number': '1234567$'})
        form.is_valid()
        assert 'account_number' in form.errors

    def test_invalid_account_number_with_wrong_number_of_chars(self):
        form = GiftWrapRequestForm(data={'account_number': '14567'})
        form.is_valid()
        assert 'account_number' in form.errors

    def test_validates_account_number_with_eight_digits(self):
        form = GiftWrapRequestForm(data={'account_number': '12345678'})
        form.is_valid()
        assert 'account_number' not in form.errors

    def test_account_number_is_required(self):
        form = GiftWrapRequestForm(data={})
        form.is_valid()
        assert 'account_number' in form.errors

    def test_email_is_required(self):
        form = GiftWrapRequestForm(data={})
        form.is_valid()
        assert 'email' in form.errors
