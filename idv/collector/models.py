from django.db import models
from django.utils import timezone


class Account(models.Model):

    email = models.EmailField()
    account_number = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'account_number')


class CredentialQuerySet(models.query.QuerySet):

    def need_moving(self):
        return self.filter(deleted_at__isnull=True)


class Credential(models.Model):

    account = models.ForeignKey(Account)
    original_filename = models.CharField(max_length=256, null=False)
    s3_key = models.CharField(max_length=30, null=False)
    upload_confirmed = models.BooleanField(default=False)
    missing_from_s3 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True)

    objects = CredentialQuerySet.as_manager()

    def mark_as_deleted(self):
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return 'Credential(pk: {}, s3_key: {})'.format(self.pk, self.s3_key)


class AccountCredentialIndex(models.Model):

    account = models.OneToOneField(Account)
    index = models.IntegerField(null=False, default=0)

    @classmethod
    def next(cls, account, save=True):
        qs = cls.objects.select_for_update()
        obj = qs.filter(account=account).get()
        obj.index += 1
        if save:
            obj.save()
        return obj.index
