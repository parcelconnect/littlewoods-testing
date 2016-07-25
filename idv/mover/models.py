from django.db import models


class MoveCommandStatus(models.Model):

    checkpoint = models.DateTimeField(
        help_text="When the 'move' command last started and was successful."
    )
