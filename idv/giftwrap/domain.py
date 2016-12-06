from .ifs import get_client_from_settings


def request_gift_wrap(giftwrap_request):
    client = get_client_from_settings()
    if giftwrap_request.divert_address:
        address = {
            'address': giftwrap_request.divert_address,
            'name': giftwrap_request.divert_contact_name,
            'phone_number': giftwrap_request.divert_contact_number,
        }
    else:
        address = None
    client.request_gift_wrap(giftwrap_request.upi, address)
