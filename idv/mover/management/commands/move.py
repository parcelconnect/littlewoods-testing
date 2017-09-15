import logging

from django.core.management.base import BaseCommand

from idv.common.decorators import retry
from idv.mover import commands as mover_commands

logger = logging.getLogger(__name__)


@retry(tries=5, delay=60)
def move():
    mover_commands.move()


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        logger.info('Starting moving credential files...')
        move()
        logger.info('Finished moving credential files.')
