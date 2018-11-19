from celery import shared_task
from dateutil import parser
from django.conf import settings

from idv.mover import mail as mover_mail
from idv.mover.commands import logger
from idv.mover.domain import get_last_move_checkpoint


@shared_task(bind=True, max_retries=4)
def send_move_report(self, since, until):
    since = parser.parse(since).date()
    until = parser.parse(until).date()

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
        self.retry(countdown=settings.SEND_REPORT_RETRY_TIME *
                   (2 ** self.request.retries))
    mover_mail.send_move_report((since, until))
