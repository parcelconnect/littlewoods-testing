import logging

from django.conf import settings

from idv.common.mail import create_mail
from idv.giftwrap.models import GiftWrapRequest

logger = logging.getLogger(__name__)


def send_new_gift_wrap_requests_notification(force=False):
    n_new_requests = GiftWrapRequest.objects.new().count()

    if n_new_requests == 0 and not force:
        logger.info('No new gift wrapping requests; no notification sent')
        return

    email = create_mail(
        subject='New Gift Wrapping Requests',
        template_prefix='new_gift_wrap_requests',
        emails=settings.GIFT_WRAPPING_REQUEST_NOTIFICATION_EMAILS,
        context={'n_new_requests': n_new_requests},
        app_name='internal'
    )
    try:
        email.send()
    except:
        logger.exception('Could not send gift-wrap requests notification')
    logger.info('Sent gift wrap requests notification')
