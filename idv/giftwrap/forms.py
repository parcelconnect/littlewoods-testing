import re

from django import forms
from django.core.exceptions import ValidationError

from .models import GiftWrapRequest

ACCOUNT_NUMBER_LENGTH = 8
UPI_LENGTH = 13
CARD_MESSAGE_LENGTH = 80


def valid_account_number(value):
    regex = r'^[a-zA-Z\d]{%s}$' % ACCOUNT_NUMBER_LENGTH
    if re.match(regex, value) is None:
        error_msg = (
            'The account number must be made of {} characters or digits.')
        raise ValidationError(error_msg.format(ACCOUNT_NUMBER_LENGTH))


def valid_upi(value):
    regex = r'^[a-zA-Z\d]{%s}$' % UPI_LENGTH
    if re.match(regex, value) is None:
        error_msg = 'The UPI must be made of {} characters or digits.'
        raise ValidationError(error_msg.format(UPI_LENGTH))


def valid_card_message(value):
    if len(value) > CARD_MESSAGE_LENGTH:
        error_msg = 'The card message must be max {} characters.'
        raise ValidationError(error_msg.format(CARD_MESSAGE_LENGTH))


class GiftWrapRequestForm(forms.ModelForm):

    class Meta:
        model = GiftWrapRequest
        fields = [
            'account_number',
            'email',
            'product_description',
            'divert_address1',
            'divert_address2',
            'divert_town',
            'divert_county',
            'divert_contact_name',
            'divert_contact_number',
            'card_message',
            'deliver_by_special_date'
        ]

    account_number = forms.CharField(
        required=True,
        validators=[valid_account_number]
    )

    card_message = forms.CharField(
        required=False,
        validators=[valid_card_message]
    )


class UPIForm(forms.ModelForm):

    class Meta:
        model = GiftWrapRequest
        fields = ['upi']

    upi = forms.CharField(
        required=True,
        validators=[valid_upi]
    )

    def clean_upi(self):
        return self.cleaned_data['upi'].upper()
