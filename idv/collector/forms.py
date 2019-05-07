import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

ACCOUNT_NUMBER_LENGTH = 8


def validate_digits_only(value):
    regex = r'^[a-zA-Z\d]{%s}$' % ACCOUNT_NUMBER_LENGTH
    if re.match(regex, value) is None:
        error_msg = 'The account number is made of {} characters/digits.'
        raise ValidationError(error_msg.format(ACCOUNT_NUMBER_LENGTH))


def validate_date_not_in_future(date):
    date_is_in_future = date > timezone.now().date()
    if date_is_in_future:
        raise ValidationError('The date is in the future.')


class AccountForm(forms.Form):

    email = forms.EmailField(required=True)
    account_number = forms.CharField(
        required=True,
        validators=[validate_digits_only]
    )
    date_1 = forms.DateField(
        required=True,
        validators=[validate_date_not_in_future]
    )
    date_2 = forms.DateField(
        required=True,
        validators=[validate_date_not_in_future]
    )
