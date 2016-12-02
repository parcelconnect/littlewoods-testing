import pytest
from django.core.urlresolvers import reverse

from idv.giftwrap.models import GiftWrapRequest


@pytest.mark.django_db
class TestRequestWrapView:

    url = reverse('giftwrap:request-wrap')

    @pytest.fixture
    def valid_post_data(self):
        return {
            'account_number': '12345678',
            'email': 'john@fastway.ie',
            'divert_contact_name': 'John Doe',
            'divert_contact_number': '123',
            'divert_address': 'Stree 18, Sometown',
            'product_description': 'Awesome present',
            'card_message': 'Best wishes'
        }

    def test_new_request_is_stored_in_db(self, client, valid_post_data):
        resp = client.post(self.url, valid_post_data)

        assert resp.status_code == 302
        assert resp['Location'] == 'success'
        assert GiftWrapRequest.objects.count() == 1

    def test_bad_form_returns_errors(self, client, valid_post_data):
        valid_post_data.pop('account_number')
        resp = client.post(self.url, valid_post_data)

        assert resp.status_code == 200
        assert 'This field is required.' in resp.content.decode()
        assert GiftWrapRequest.objects.count() == 0
