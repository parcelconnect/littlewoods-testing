import logging

from celery import shared_task
from dateutil import parser
from django.conf import settings

from idv.mover import mail as mover_mail
from idv.mover.domain import get_last_move_checkpoint

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=4)
def send_move_report(self, since, until):
    since = parser.parse(since).date()
    until = parser.parse(until).date()

    move_checkpoint = get_last_move_checkpoint()
    if not move_checkpoint:
        raise ValueError(
            "Cannot generate report for ({since}-{until}). "
            "The move command seems to have never run successfully."
        )
    if until > move_checkpoint.date():
        checkpoint_str = move_checkpoint.strftime("%Y-%m-%d %H:%M:%S")
        logger.error(f"Cannot generate report for ({since}, {until}). "
                     f"Last successful `move` ran at {checkpoint_str}.")
        self.retry(countdown=settings.SEND_REPORT_RETRY_TIME *
                   (2 ** self.request.retries))
    mover_mail.send_move_report((since, until))
    logger.info(f'Success sending report for ({since}, {until}).')
