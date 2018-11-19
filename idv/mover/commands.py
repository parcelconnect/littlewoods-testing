import logging

from idv.collector.models import Credential

from .contextmanagers import log_move
from .domain import move_credential_files

logger = logging.getLogger(__name__)


def move():
    with log_move() as started_dt:
        creds = Credential.objects.created_before(started_dt).need_moving()
        move_credential_files(creds)
