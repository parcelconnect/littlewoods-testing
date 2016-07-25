from django.core.management.base import BaseCommand

from idv.common.decorators import retry
from idv.mover import commands as mover_commands


@retry(tries=5, delay=60)
def move():
    mover_commands.move()


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        move()
