import re

from django import forms
from django.core.exceptions import ValidationError

from .models import GiftWrapRequest


ACCOUNT_NUMBER_LENGTH = 8


def valid_account_number(value):
    regex = r'^[a-zA-Z\d]{%s}$' % ACCOUNT_NUMBER_LENGTH
    if re.match(regex, value) is None:
        error_msg = 'The account number is made of {} characters/digits.'
        raise ValidationError(error_msg.format(ACCOUNT_NUMBER_LENGTH))


class GiftWrapRequestForm(forms.ModelForm):

    class Meta:
        model = GiftWrapRequest
        fields = [
            'account_number', 'email', 'product_description',
            'divert_address', 'divert_contact_name', 'divert_contact_number',
            'card_message'
        ]

    account_number = forms.CharField(
        required=True,
        validators=[valid_account_number]
    )


class EpackSearchForm(forms.ModelForm):

    class Meta:
        model = GiftWrapRequest
        fields = [
            'upi'
        ]

    upi = forms.CharField(
        required=True,
    )
