import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from idv.giftwrap.management.commands.send_upi_report import (
    get_successful_upis, send_report_email
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    report_date = timezone.now().date() - timedelta(day=1)
    formatted_date = report_date.strftime("%d of %B")

    help = 'Send report on successful upis'

    def handle(self, *args, **kwargs):
        succesful_upis = get_successful_upis(self.report_date)
        logger.info('Sending report on succesful upis on {}...'
                    .format(self.formatted_date))
        send_report_email(succesful_upis)
        logger.info('Success sending report.')
