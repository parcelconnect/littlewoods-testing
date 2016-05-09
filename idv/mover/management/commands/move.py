from django.core.management.base import BaseCommand

from idv.collector.models import Credential
from idv.mover.domain import move_credential_files


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        credentials = Credential.objects.need_moving()
        move_credential_files(credentials)
