from .ifs import get_client_from_settings


def request_gift_wrap(gift_wrap_request):
    client = get_client_from_settings()
    if gift_wrap_request.divert_address:
        address = {
            'address': gift_wrap_request.divert_address,
            'name': gift_wrap_request.divert_contact_name,
            'phone_number': gift_wrap_request.divert_contact_number,
        }
    else:
        address = None
    client.request_gift_wrap(gift_wrap_request.upi, address)
