import logging

from celery import shared_task

from idv.collector.models import Credential

from . import mail as mover_mail
from .contextmanagers import log_move
from .domain import get_last_move_checkpoint, move_credential_files

logger = logging.getLogger(__name__)


def move():
    with log_move() as started_dt:
        creds = Credential.objects.created_before(started_dt).need_moving()
        move_credential_files(creds)


@shared_task(bind=True, max_retries=4)
def send_move_report(self, since, until):
    move_checkpoint = get_last_move_checkpoint()
    if not move_checkpoint:
        raise ValueError(
            "Cannot generate report for [{since}-{until}). "
            "The move command seems to have never run successfully."
        )
    if until > move_checkpoint.date():
        checkpoint_str = move_checkpoint.strftime("%Y-%m-%d %H:%M:%S")
        logger.error("Cannot generate report for [{since}, {until}). "
                     "Last successful `move` ran at {checkpoint}."
                     .format(since=since, until=until,
                             checkpoint=checkpoint_str))
        self.retry(countdown=(10 * 60) * (2 ** self.request.retries))
    mover_mail.send_move_report((since, until))
