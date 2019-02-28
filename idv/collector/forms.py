import re

from django import forms
from django.core.exceptions import ValidationError

ACCOUNT_NUMBER_LENGTH = 8


def validate_digits_only(value):
    regex = r'^[a-zA-Z\d]{%s}$' % ACCOUNT_NUMBER_LENGTH
    if re.match(regex, value) is None:
        error_msg = 'The account number is made of {} characters/digits.'
        raise ValidationError(error_msg.format(ACCOUNT_NUMBER_LENGTH))


class AccountForm(forms.Form):

    email = forms.EmailField(required=True)
    account_number = forms.CharField(
        required=True,
        validators=[validate_digits_only]
    )
    # TODO: change dates to be required when removing lwi-new-design switch.
    date_1 = forms.DateField(required=False)
    date_2 = forms.DateField(required=False)
