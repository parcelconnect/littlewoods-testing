from .ifs import get_client_from_settings, IFSAPIError, TooLateError
from .models import GiftWrapRequest


def _build_divert_address(gift_wrap_request):
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
    return address


def request_gift_wrap(instance):
    address = _build_divert_address(instance)
    client = get_client_from_settings()
    try:
        client.request_gift_wrap(instance.upi, address)
    except TooLateError:
        instance.mark_as_failed()
    except IFSAPIError:
        instance.mark_as_error()
    else:
        instance.mark_as_success()
    return instance.status


def update_upi(instance, upi):
    instance.upi = upi
    instance.save()


def get_orders_for_upi(upi):
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
