from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from idv.common.decorators import retry
from idv.common.mail import create_mail
from idv.giftwrap.models import GiftWrapRequest


def get_successful_upis(created_when):
    return GiftWrapRequest.objects.created_at(created_when).filter(
        status="success").values_list("upi", flat=True)


@retry(tries=5, delay=60)
def send_report_email(data):
    """
     Creates an email report for the successful upis for the previous day
    """

    report_date = timezone.now().date() - timedelta(day=1)
    formatted_date = report_date.strftime("%d of %B")
    successful_upis = get_successful_upis(report_date)
    recipients = settings.UPI_REPORT_RECIPIENTS
    subject = """Littlewoods ID&V Gift Wrapping Requests
        processed on the {}""".format(formatted_date)
    message = """There were {} successful gift wrapping requests
        processed on the {}.\n""".format(len(successful_upis), formatted_date)

    for upi in successful_upis:
        message = message + upi + "\n"

    msg = create_mail(
        subject=subject,
        context=message,
        emails=recipients,
    )
    msg.send()
