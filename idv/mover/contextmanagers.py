from contextlib import contextmanager

from django.utils import timezone

from .models import MoveCommandStatus


@contextmanager
def log_move():
    try:
        status = MoveCommandStatus.objects.get()
    except MoveCommandStatus.DoesNotExist:
        status = MoveCommandStatus()

    started_at = timezone.now()
    yield started_at
    status.checkpoint = started_at
    status.save()
