from django.db import models


class Account(models.Model):

    email = models.EmailField()
    account_number = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'account_number')


class Credential(models.Model):

    original_filename = models.CharField(max_length=256, null=False)
    s3_key = models.CharField(max_length=5, null=False)
    upload_confirmed = models.BooleanField(default=False)
    account = models.ForeignKey(Account)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)
