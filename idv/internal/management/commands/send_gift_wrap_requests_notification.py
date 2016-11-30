from django.core.management.base import BaseCommand

from ..commands import send_new_gift_wrap_requests_notification


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        send_new_gift_wrap_requests_notification()
