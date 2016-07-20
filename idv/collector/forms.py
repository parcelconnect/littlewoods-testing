import re

from django import forms
from django.core.exceptions import ValidationError


ACCOUNT_NUMBER_LENGTH = 8


def validate_digits_only(value):
    regex = r'^\d{%s}$' % ACCOUNT_NUMBER_LENGTH
    if re.match(regex, value) is None:
        error_msg = 'The account number is made of {} digits.'.format(
            ACCOUNT_NUMBER_LENGTH
        )
        raise ValidationError(error_msg)


class AccountForm(forms.Form):

    email = forms.EmailField(required=True)
    account_number = forms.CharField(
        required=True,
        validators=[validate_digits_only]
    )
