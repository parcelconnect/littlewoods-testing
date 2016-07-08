from django import forms


class AccountForm(forms.Form):

    email = forms.EmailField(required=True)
    account_number = forms.CharField(max_length=30, required=True)
