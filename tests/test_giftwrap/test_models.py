import pytest

from idv.giftwrap.models import GiftWrapRequest


@pytest.mark.django_db
class TestGiftWrapRequest:

    def test_new_returns_expected_request(
            self, request_success, request_new, request_failed, request_error,
            request_rejected):
        query = GiftWrapRequest.objects.new()

        assert query.count() == 1
        assert query.first() == request_new

    def test_success_returns_expected_request(
            self, request_success, request_new, request_failed, request_error,
            request_rejected):
        query = GiftWrapRequest.objects.success()

        assert query.count() == 1
        assert query.first() == request_success

    def test_error_returns_expected_request(
            self, request_success, request_new, request_failed, request_error,
            request_rejected):
        query = GiftWrapRequest.objects.error()

        assert query.count() == 1
        assert query.first() == request_error

    def test_rejected_returns_expected_request(
            self, request_success, request_new, request_failed, request_error,
            request_rejected):
        query = GiftWrapRequest.objects.rejected()

        assert query.count() == 1
        assert query.first() == request_rejected

    def test_failed_returns_expected_request(
            self, request_success, request_new, request_failed, request_error,
            request_rejected):
        query = GiftWrapRequest.objects.failed()

        assert query.count() == 1
        assert query.first() == request_failed

    def test_str_returns_expected_string(self, request_success):
        account = request_success.account_number
        status = request_success.status
        expected_string = f'Account: {account}, Status: {status}'

        assert str(request_success) == expected_string
