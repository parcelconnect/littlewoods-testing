import re

from django import forms
from django.core.exceptions import ValidationError

from .models import GiftWrapRequest


ACCOUNT_NUMBER_LENGTH = 8


def validate_digits_only(value):
    regex = r'^[a-zA-Z\d]{%s}$' % ACCOUNT_NUMBER_LENGTH
    if re.match(regex, value) is None:
        error_msg = 'The account number is made of {} characters/digits.'
        raise ValidationError(error_msg.format(ACCOUNT_NUMBER_LENGTH))


class GiftWrapRequestForm(forms.ModelForm):

    class Meta:
        model = GiftWrapRequest
        fields = [
            'account_number', 'email', 'order_number', 'product_description',
            'divert_address', 'divert_contact_name', 'divert_contact_number',
            'card_message'
        ]

    email = forms.EmailField(required=True)
    account_number = forms.CharField(
        required=True,
        validators=[validate_digits_only]
    )