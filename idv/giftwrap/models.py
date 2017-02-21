from django.db import models

from idv.common.utils import enum_to_choices

from .types import DeliverBySpecialDate, GiftWrapRequestStatus


class GiftWrapRequestQuerySet(models.query.QuerySet):

    def new(self):
        return self.filter(status=GiftWrapRequestStatus.New.value)

    def success(self):
        return self.filter(status=GiftWrapRequestStatus.Success.value)

    def failed(self):
        return self.filter(status=GiftWrapRequestStatus.Failed.value)

    def error(self):
        return self.filter(status=GiftWrapRequestStatus.Error.value)

    def rejected(self):
        return self.filter(status=GiftWrapRequestStatus.Rejected.value)

    def with_upi(self, upi):
        return self.filter(upi=upi)

    def created_on(self, date):
        return self.filter(
            created_at__year=date.year,
            created_at__month=date.month,
            created_at__day=date.day
        )

    def created_from(self, date):
        return self.filter(
            created_at__gte=date
        )

    def created_until(self, date):
        return self.filter(
            created_at__lte=date
        )

    def modified_on(self, date):
        return self.filter(
            updated_at__year=date.year,
            updated_at__month=date.month,
            updated_at__day=date.day
        )

    def modified_until(self, date):
        return self.filter(
            updated_at__lte=date
        )

    def modified_from(self, date):
        return self.filter(
            updated_at__gte=date
        )


class GiftWrapRequest(models.Model):

    account_number = models.CharField(max_length=8)
    email = models.EmailField()

    product_description = models.TextField()
    upi = models.CharField(max_length=30, blank=True)

    divert_address1 = models.CharField(max_length=150, blank=True)
    divert_address2 = models.CharField(max_length=150, blank=True)
    divert_town = models.CharField(max_length=100, blank=True)
    divert_county = models.CharField(max_length=50, blank=True)
    divert_contact_name = models.CharField(max_length=80, blank=True)
    divert_contact_number = models.CharField(max_length=80, blank=True)
    deliver_by_special_date = models.CharField(
        max_length=8,
        choices=enum_to_choices(DeliverBySpecialDate),
    )

    card_message = models.CharField(max_length=80, blank=True)

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

    def mark_as_rejected(gw_request):
        gw_request.status = GiftWrapRequestStatus.Rejected.value
        gw_request.save()
