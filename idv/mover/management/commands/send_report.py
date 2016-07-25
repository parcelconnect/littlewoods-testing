from datetime import datetime, timedelta
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils import timezone

from idv.mover.commands import send_move_report


class Command(BaseCommand):

    DATE_FORMAT = '%Y-%m-%d'

    help = 'Send report on files uploaded/moved'

    option_list = BaseCommand.option_list + (
        make_option(
            '--since', dest='since',
            help=('Starting date to generate report for. '
                  'Format: %Y-%m-%d. Defaults to "yesterday".')
        ),
        make_option(
            '--until', dest='until',
            help=('Ending date to generate report for. '
                  'Format: %Y-%m-%d. Defaults to "start of today".')
        ),
    )

    def handle(self, *args, **kwargs):
        since = self.get_since_date(kwargs.get('since'))
        until = self.get_until_date(kwargs.get('until'))
        send_move_report(since, until)

    def get_since_date(self, date):
        date_obj = None
        if date is None:
            today = timezone.now().date()
            date_obj = today - timedelta(days=1)
        else:
            date_obj = datetime.strptime(date, self.DATE_FORMAT).date()
        return date_obj

    def get_until_date(self, date):
        date_obj = None
        if date is None:
            date_obj = timezone.now().date()
        else:
            date_obj = datetime.strptime(date, self.DATE_FORMAT).date()
        return date_obj
