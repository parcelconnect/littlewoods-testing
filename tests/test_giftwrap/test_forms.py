from idv.giftwrap.forms import GiftWrapRequestForm


class TestGiftWrapRequestForm:

    def test_is_valid_returns_true_when_all_required_fields_given(self):
        form = GiftWrapRequestForm(
            data={
                'account_number': '12345678',
                'email': 'john@fastway.ie',
                'divert_contact_name': 'John Doe',
                'divert_contact_number': '123',
                'divert_address1': 'Street 18',
                'divert_town': 'Sometown',
                'product_description': 'Awesome present',
                'card_message': 'Best wishes'
            }
        )
        assert form.is_valid(), form.errors

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
