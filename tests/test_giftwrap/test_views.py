import pytest
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from idv.giftwrap.models import GiftWrapRequest, GiftWrapRequestStatus


@pytest.fixture
def user():
    return User.objects.create_user(username='lwuser', password='123456')


@pytest.fixture
def loggedin_user(client, user):
    assert client.login(username=user.username, password='123456')
    return user


@pytest.fixture
def request_new():
    return GiftWrapRequest.objects.create(account_number="A01")


@pytest.fixture
def request_failed():
    return GiftWrapRequest.objects.create(
        account_number="A02",
        status=GiftWrapRequestStatus.Failed.value
    )


@pytest.fixture
def request_error():
    return GiftWrapRequest.objects.create(
        account_number="A02",
        status=GiftWrapRequestStatus.Error.value
    )


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
            'divert_address1': 'Street 18',
            'divert_town': 'Sometown',
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


@pytest.mark.django_db
class TestLWIRequestsView:

    url = reverse('giftwrap:lwi-requests')

    def test_it_redirects_to_login_page_when_not_authenticated(self, client):
        resp = client.get(self.url)

        assert resp.status_code == 302
        assert resp['Location'] == (
            '/gift-wrapping/internal-login/?next=/gift-wrapping/requests/')

    def test_it_displays_requests_when_status_is_new(
            self, loggedin_user, client, request_new, request_failed):
        resp = client.get(self.url)

        assert resp.status_code == 200
        response = resp.content.decode()
        assert request_new.account_number in response
        assert request_failed.account_number not in response

    def test_it_displays_requests_when_status_is_error(
            self, loggedin_user, client, request_error):
        resp = client.get(self.url)

        assert resp.status_code == 200
        response = resp.content.decode()
        assert request_error.account_number in response
