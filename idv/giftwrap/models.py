from django.db import models

from idv.common.utils import enum_to_choices

from .types import GiftWrapRequestStatus


class GiftWrapRequestQuerySet(models.query.QuerySet):

    def new(self):
        return self.filter(status=GiftWrapRequestStatus.New.value)

    def success(self):
        return self.filter(status=GiftWrapRequestStatus.Success.value)

    def failed(self):
        return self.filter(status=GiftWrapRequestStatus.Failed.value)

    def error(self):
        return self.filter(status=GiftWrapRequestStatus.Failed.value)


class GiftWrapRequest(models.Model):

    account_number = models.CharField(max_length=8)
    email = models.EmailField()

    product_description = models.TextField()
    upi = models.CharField(max_length=30, blank=True, default='')

    divert_address = models.CharField(max_length=80, blank=True, default='')
    divert_contact_name = models.CharField(
        max_length=80,
        blank=True,
        default=''
    )
    divert_contact_number = models.CharField(
        max_length=80,
        blank=True,
        default=''
    )

    card_message = models.TextField()

    status = models.CharField(
        max_length=8,
        choices=enum_to_choices(GiftWrapRequestStatus),
        default=GiftWrapRequestStatus.New.value,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GiftWrapRequestQuerySet.as_manager()

    def __str__(self):
        return (
            'Account: {account}, Status: {status}'
            .format(account=self.account_number, status=self.status)
        )

    def mark_as_success(self):
        self.status = GiftWrapRequestStatus.Success.value
        self.save()

    def mark_as_failed(self):
        self.status = GiftWrapRequestStatus.Failed.value
        self.save()

    def mark_as_error(self):
        self.status = GiftWrapRequestStatus.Error.value
        self.save()
