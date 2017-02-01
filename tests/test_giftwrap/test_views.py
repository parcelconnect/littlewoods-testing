from unittest import mock

import pytest
import responses
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from idv.giftwrap import ifs
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
        account_number="A03",
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
            'card_message': 'Best wishes',
            'deliver_by_special_date': 'Before'
        }

    @pytest.fixture
    def data_with_invalid_card_message(self, valid_post_data):
        invalid_post_data = valid_post_data
        invalid_post_data['card_message'] = 'Two roads diverged in a yellow wood\
        , And sorry I could not travel both And be one traveler, long I stood\
         And looked down one as far as I could To where it bent in\
         the undergrowth;'
        return invalid_post_data

    def test_it_displays_the_special_date_when_set(self, client, settings):
        settings.SPECIAL_DATE_NAME = "Christmas"
        resp = client.get(self.url)

        assert resp.status_code == 200
        assert resp.context['special_date_name'] == "Christmas"
        assert settings.SPECIAL_DATE_IMAGE[
            "Christmas"] in resp.content.decode()
        assert 'Christmas' in resp.content.decode()

    def test_it_hides_the_special_date_when_not_set(self, client, settings):
        settings.SPECIAL_DATE_NAME = ""
        resp = client.get(self.url)

        assert resp.status_code == 200
        assert resp.context['special_date_name'] == ""
        assert settings.SPECIAL_DATE_IMAGE[
            "Christmas"] in resp.content.decode()
        assert 'Christmas' not in resp.content.decode()

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

    def test_max_char_error_message_displays(
            self, client, data_with_invalid_card_message):
        data_with_invalid_card_message.pop('account_number')
        resp = client.post(self.url, data_with_invalid_card_message)

        assert resp.status_code == 200
        assert 'The card message must be max' in resp.content.decode()
        assert GiftWrapRequest.objects.count() == 0


@pytest.mark.django_db
class TestLWIRequestsView:

    url = reverse('giftwrap:lwi-requests')

    def test_it_redirects_to_login_page_when_not_authenticated(self, client):
        resp = client.get(self.url)

        assert resp.status_code == 302
        login_url = reverse('giftwrap:lwi-login')
        expected_redirect_url = "{}?next={}".format(login_url, self.url)
        assert resp['Location'] == expected_redirect_url

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


@pytest.mark.django_db
class TestLWIRequestDetailsView:

    @pytest.fixture
    def valid_upi(self):
        return "A"*13

    def test_it_redirects_to_login_page_when_not_authenticated(
            self, client, request_new):
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.get(url)

        assert resp.status_code == 302
        login_url = reverse('giftwrap:lwi-login')
        expected_redirect_url = "{}?next={}".format(login_url, url)
        assert resp['Location'] == expected_redirect_url

    def test_it_displays_details_when_using_get(
            self, loggedin_user, client, request_new):
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.get(url)

        assert resp.status_code == 200
        response = resp.content.decode()
        assert request_new.account_number in response
        assert request_new.card_message in response

    def test_it_displays_the_special_date_when_set(
            self, loggedin_user, client, request_new, settings):
        settings.SPECIAL_DATE_NAME = "Christmas"
        request_new.deliver_by_special_date = True
        request_new.save()
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.get(url)

        assert resp.status_code == 200
        assert resp.context['special_date_name'] == "Christmas"
        assert settings.SPECIAL_DATE_IMAGE[
            "Christmas"] in resp.content.decode()
        assert 'Deliver this parcel' in resp.content.decode()

    def test_it_hides_the_special_date_when_not_set(
            self, loggedin_user, client, request_new, settings):
        settings.SPECIAL_DATE_NAME = ""
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.get(url)

        assert resp.status_code == 200
        assert resp.context['special_date_name'] == ""
        assert settings.SPECIAL_DATE_IMAGE[
            "Christmas"] in resp.content.decode()
        assert 'Deliver this parcel' not in resp.content.decode()

    @responses.activate
    def test_it_returns_400_and_displays_error_msg_when_post_has_no_upi_value(
            self, loggedin_user, client, request_new):
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.post(url, data={})

        assert resp.status_code == 400
        assert 'This field is required.' in resp.content.decode()

    @mock.patch.object(
        ifs.Client,
        'request_gift_wrap',
        return_value=True
    )
    @responses.activate
    def test_it_returns_201_and_displays_success_msg_when_post_succeeds(
            self, mock_request, client_settings, loggedin_user, client,
            request_new, valid_upi):
        mock_request.return_value = True
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.post(url, data={'upi': valid_upi})

        assert resp.status_code == 302
        assert resp['Location'] == reverse('giftwrap:lwi-requests')

    @mock.patch.object(
        ifs.Client,
        'request_gift_wrap',
        side_effect=ifs.TooLateError('Late. Yes')
    )
    @responses.activate
    def test_it_returns_204_and_displays_failed_msg_when_post_fails(
            self, mock_request, client_settings, loggedin_user, client,
            request_new, valid_upi):
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.post(url, data={'upi': valid_upi})

        assert resp.status_code == 202
        assert 'Request is too late' in resp.content.decode()

    @mock.patch.object(
        ifs.Client,
        'request_gift_wrap',
        side_effect=ifs.IFSAPIError('Catastrophe')
    )
    @responses.activate
    def test_it_returns_204_and_displays_error_msg_when_post_fails(
            self, mock_request, client_settings, loggedin_user, client,
            request_new, valid_upi):
        mock_request.side_effect = ifs.IFSAPIError('Catastrophe')
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.post(url, data={'upi': valid_upi})

        assert resp.status_code == 202
        assert 'Request to IFS failed' in resp.content.decode()

    def test_if_status_changes_to_rejected_when_delete_method_is_used(
            self, request_new, loggedin_user, client):
        url = reverse('giftwrap:lwi-request-details',
                      kwargs={'pk': request_new.pk})
        resp = client.delete(url)
        assert resp.status_code == 200


@pytest.mark.django_db
class TestEpackSearchView:

    url = reverse('giftwrap:epack-search')

    def test_it_redirects_to_login_page_when_not_authenticated(self, client):
        resp = client.get(self.url)

        assert resp.status_code == 302
        login_url = reverse('giftwrap:epack-login')
        expected_redirect_url = "{}?next={}".format(login_url, self.url)
        assert resp['Location'] == expected_redirect_url

    def test_it_does_not_set_input_value_and_shows_no_errors_if_upi_not_given(
            self, loggedin_user, client):
        resp = client.get(self.url)

        assert resp.status_code == 200
        assert 'Enter UPI' in resp.content.decode()
        assert 'value="' not in resp.content.decode()
        assert 'alert' not in resp.content.decode()

    def test_it_displays_details_when_upi_found(
            self, loggedin_user, client, request_success, settings):
        settings.SPECIAL_DATE_NAME = "Christmas"
        request_success.deliver_by_special_date = True
        request_success.save()
        resp = client.get(self.url, data={'upi': request_success.upi})

        assert resp.status_code == 200
        assert resp.context['special_date_name'] == "Christmas"
        assert settings.SPECIAL_DATE_IMAGE[
            "Christmas"] in resp.content.decode()
        assert 'UPI:' + request_success.upi in resp.content.decode()
        assert 'Lovely' in resp.content.decode()
        assert "Deliver this parcel" in resp.content.decode()

    def test_it_does_not_display_special_date_when_not_set(
            self, loggedin_user, client, request_success, settings):
        settings.SPECIAL_DATE_NAME = ""
        resp = client.get(self.url, data={'upi': request_success.upi})

        assert resp.status_code == 200
        assert resp.context['special_date_name'] == ""
        assert settings.SPECIAL_DATE_IMAGE[
            "Christmas"] in resp.content.decode()
        assert 'UPI:' + request_success.upi in resp.content.decode()
        assert "Deliver this parcel" not in resp.content.decode()

    def test_it_displays_error_msg_when_upi_not_found(
            self, loggedin_user, client):
        resp = client.get(self.url, data={'upi': 'B' * 13})

        assert resp.status_code == 200
        assert 'UPI not found.' in resp.content.decode()

    def test_it_displays_error_when_upi_present_but_status_new(
            self, loggedin_user, client, request_new):
        request_new.upi = "B" * 13
        request_new.card_message = "Lovely"
        request_new.save()

        resp = client.get(self.url, data={'upi': request_new.upi})

        assert resp.status_code == 200
        response = resp.content.decode()
        assert 'UPI not found.' in response
        assert 'value="{}"'.format(request_new.upi) in response
        assert 'Lovely' not in response

    def test_it_displays_error_msg_when_upi_invalid(
            self, loggedin_user, client):
        resp = client.get(self.url, data={'upi': 'A' * 18})

        assert resp.status_code == 200
        invalid_upi_error = 'The UPI must be made of 13 characters or digits.'
        assert invalid_upi_error in resp.content.decode()
