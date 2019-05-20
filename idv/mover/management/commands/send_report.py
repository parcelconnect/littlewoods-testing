import argparse
import logging
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from idv.mover.tasks import send_move_report

logger = logging.getLogger(__name__)


def valid_date(date_string):
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(date_string)
        raise argparse.ArgumentTypeError(msg)


class Command(BaseCommand):
    DATE_FORMAT = '%Y-%m-%d'
    help = 'Send report on files uploaded/moved'

    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--since',
            action='store',
            type=valid_date,
            help=('Starting date to generate report for '
                  '- format YYYY-MM-DD. Defaults to "yesterday".')
        )
        parser.add_argument(
            '-u',
            '--until',
            action='store',
            type=valid_date,
            help=('Ending date to generate report for '
                  '- format YYYY-MM-DD. Defaults to "start of today".')
        )

    def handle(self, *args, **kwargs):
        if kwargs.get('since'):
            since = kwargs['since']
        else:
            since = timezone.now().date() - timedelta(days=1)

        if kwargs.get('until'):
            until = kwargs['until']
        else:
            until = timezone.now().date()

        logger.info('Sending report on files uploaded from {} to {}...'
                    .format(since, until))
        send_move_report.delay(since, until)
