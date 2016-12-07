from .ifs import get_client_from_settings, IFSAPIError, TooLateError
from .models import GiftWrapRequest


def request_gift_wrap(gift_wrap_request):
    client = get_client_from_settings()
    if gift_wrap_request.divert_address1:
        address = {
            "address1": gift_wrap_request.divert_address1,
            "address2": gift_wrap_request.divert_address2,
            "town": gift_wrap_request.divert_town,
            "county": gift_wrap_request.divert_county,
            'name': gift_wrap_request.divert_contact_name,
            'phone_number': gift_wrap_request.divert_contact_number,
        }
    else:
        address = None
    client.request_gift_wrap(gift_wrap_request.upi, address)


def make_request_to_ifs(self, upi, instance):
    instance.upi = upi
    try:
        request_gift_wrap(instance)
    except TooLateError:
        instance.mark_as_failed()
    except IFSAPIError:
        instance.mark_as_error()
    else:
        instance.mark_as_success()
    return instance.status


def get_orders_for_upi(self, upi):
    return (
        GiftWrapRequest.objects
        .success()
        .with_upi(upi)
        .values(
            'divert_contact_name',
            'divert_address1',
            'divert_address2',
            'divert_town',
            'divert_county',
            'card_message'
        )
    )
