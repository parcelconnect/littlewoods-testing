from django.core.management.base import BaseCommand

from idv.collector.models import Credential
from idv.mover.domain import move_credential_files
from idv.common.decorators import retry


@retry(tries=5, delay=60)
def move():
    credentials = Credential.objects.need_moving()
    move_credential_files(credentials)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        move()
