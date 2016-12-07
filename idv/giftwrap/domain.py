from .ifs import get_client_from_settings


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
