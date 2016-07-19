from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils import timezone

from .const import CredentialStatus
from .util import enum_to_choices


class Account(models.Model):
    """
    Represents a Littlewoods account, identified by `email` and
    `account_number` used in the Littlewoods service.
    """
    email = models.EmailField()
    account_number = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('email', 'account_number')

    def __str__(self):
        return 'Account(email: {}, account_number: {})'.format(
            self.email,
            self.account_number
        )


class CredentialQuerySet(models.query.QuerySet):

    def need_moving(self):
        return self.filter(
            Q(status=CredentialStatus.Unchecked.value) |
            Q(status=CredentialStatus.Found.value)
        )

    def created_between(self, date_range):
        since, until = date_range
        since = datetime(since.year, since.month, since.day, 0, 0, 0, 0)
        since = timezone.make_aware(since)
        until = datetime(until.year, until.month, until.day, 0, 0, 0, 0)
        until = timezone.make_aware(until)
        return self.filter(created_at__range=(since, until))

    def not_found(self):
        return self.filter(status=CredentialStatus.NotFound.value)

    def moved(self):
        return self.filter(status=CredentialStatus.Moved.value)


class Credential(models.Model):
    """
    Represents a file that a littlewoods user uploads to prove his identity.
    """
    account = models.ForeignKey(Account)
    original_filename = models.CharField(max_length=256, null=False)
    s3_key = models.CharField(max_length=30, null=False)
    status = models.IntegerField(
        choices=enum_to_choices(CredentialStatus),
        default=CredentialStatus.Unchecked.value
    )
    created_at = models.DateTimeField(auto_now_add=True)
    copied_at = models.DateTimeField(
        null=True,
        help_text='When it was copied from Fastway S3 to LW SFTP'
    )
    deleted_at = models.DateTimeField(null=True)

    objects = CredentialQuerySet.as_manager()

    def mark_as_found(self):
        self.status = CredentialStatus.Found.value
        self.save()

    def mark_as_not_found(self):
        self.status = CredentialStatus.NotFound.value
        self.save()

    def mark_as_copied(self):
        self.status = CredentialStatus.Copied.value
        self.copied_at = timezone.now()
        self.save()

    def mark_as_moved(self):
        self.status = CredentialStatus.Moved.value
        self.deleted_at = timezone.now()
        self.save()

    def __str__(self):
        return 'Credential(pk: {}, s3_key: {})'.format(self.pk, self.s3_key)


class AccountCredentialIndex(models.Model):
    """
    Used internally to generate an s3 key. For example, a user with a LW
    account number 1234 may want to upload 2 jpeg files. Those files will end
    up being named [prefix]_1.jpg [prefix_2]. Those two numbers just before
    the extension are generated from this model.
    """
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
