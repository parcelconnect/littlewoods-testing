from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from idv.common.decorators import retry
from idv.giftwrap.models import GiftWrapRequest, GiftWrapRequestStatus


def get_successful_upis_for_day(created_when):
    return GiftWrapRequest.objects.filter(
        created_at__year=created_when.year,
        created_at__month=created_when.month,
        created_at__day=created_when.day,
        status=GiftWrapRequestStatus.Success.value
    ).values_list("upi", flat=True)


@retry(tries=5, delay=60)
def send_report_email(run_report_date):
    """
     Creates an email report for the successful upis for the previous day
    """

    formatted_date = run_report_date.strftime("%dth of %B")
    successful_upis = get_successful_upis_for_day(run_report_date)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipients = settings.UPI_REPORT_RECIPIENTS
    subject = ('Littlewoods ID&V Gift Wrapping Requests processed on the {}'
               .format(formatted_date))
    message = ('There were {} successful gift wrapping requests processed on '
               'the {}.\n'.format(len(successful_upis), formatted_date))

    for upi in successful_upis:
        message = message + upi + "\n"

    msg = EmailMultiAlternatives(subject, message, from_email, recipients)
    msg.send()
