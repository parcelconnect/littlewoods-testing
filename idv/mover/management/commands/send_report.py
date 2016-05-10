from datetime import datetime, timedelta
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils import timezone

from idv.mover.mail import send_daily_report


class Command(BaseCommand):

    DATE_FORMAT = '%Y-%m-%d'

    help = 'Send daily report on files uploaded/moved'

    option_list = BaseCommand.option_list + (
        make_option(
            '--date', dest='date',
            help=('Date to generate report for. '
                  'Format: %Y-%m-%d. Defaults to "yesterday".')
        ),
    )

    def handle(self, *args, **kwargs):
        date = self.get_date(kwargs.get('date'))
        send_daily_report(date)

    def get_date(self, date):
        date_obj = None
        if date is None:
            today = timezone.now().date()
            date_obj = today - timedelta(days=1)
        else:
            date_obj = datetime.strptime(date, self.DATE_FORMAT)
        return date_obj
