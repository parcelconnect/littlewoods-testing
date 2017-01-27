import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from idv.giftwrap.reporting import send_report_email

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Send report on successful upis'

    def handle(self, *args, **kwargs):
        report_date = timezone.now().date() - timedelta(days=1)
        formatted_date = report_date.strftime("%d of %B")
        logger.info('Sending report on succesful upis on {}...'
                    .format(formatted_date))
        send_report_email(report_date)
        logger.info('Success sending report.')
