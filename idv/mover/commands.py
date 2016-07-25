from idv.collector.models import Credential

from . import mail as mover_mail
from .contextmanagers import log_move
from .domain import get_last_move_checkpoint, move_credential_files


def move():
    with log_move() as started_dt:
        creds = Credential.objects.created_before(started_dt).need_moving()
        move_credential_files(creds)


def send_move_report(since, until):
    move_checkpoint = get_last_move_checkpoint()
    if not move_checkpoint:
        raise ValueError(
            "Cannot generate report for [{since}-{until}). "
            "The move command seems to have never run successfully."
        )
    if until > move_checkpoint.date():
        checkpoint_str = move_checkpoint.strftime("%Y-%m-%d %H:%M:%S")
        raise ValueError(
            "Cannot generate report for [{since}, {until}). "
            "Last successful `move` ran at {checkpoint}."
            .format(since=since, until=until, checkpoint=checkpoint_str)
        )
    mover_mail.send_move_report((since, until))
