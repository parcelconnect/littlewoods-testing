from datetime import datetime, time

from dateutil.parser import parse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from pytz import timezone

from idv.common.decorators import retry
from idv.giftwrap.models import GiftWrapRequest

FROM_DATE = parse(settings.RUN_REPORT_FROM_DATE)


def _get_success_upis_for_day(date):
    return (
        GiftWrapRequest.objects
        .modified_on(date)
        .success()
        .values_list("upi", flat=True)
    )


def _get_success_upis_until_date(end_datetime):
    return (
        GiftWrapRequest.objects
        .modified_from(FROM_DATE)
        .modified_until(end_datetime)
        .success()
        .values_list("upi", flat=True)
    )


def _request_count_for_day(date):
    return GiftWrapRequest.objects.created_on(date).count()


def _request_count_until_date(end_datetime):
    return (
        GiftWrapRequest.objects
        .created_from(FROM_DATE)
        .created_until(end_datetime)
        .count()
    )


def _build_message(successful_yesterday, successful_until_yesterday,
                   request_count_yesterday, request_count_until_date, date):
    message = ""
    message = message + (
        "There were {} gift wrapping requests processed on {}."
        "\r\n".format(len(successful_yesterday), date)
    )

    for upi in successful_yesterday:
        message = message + upi + "\r\n"

    message = message + (
        "\r\n\r\n"
        "There were {} gift wrapping requests processed until {}."
        "\r\n".format(len(successful_until_yesterday), date)
    )

    for upi in successful_until_yesterday:
        message = message + upi + "\r\n"

    message = message + (
        "\r\n\r\n"
        "There were {} customer gift wrapping requests on {}."
        "\r\n".format(request_count_yesterday, date)
    )

    message = message + (
        "\r\n\r\n"
        "There were {} customer gift wrapping requests made until {}."
        "\r\n".format(request_count_until_date, date)
    )

    return message


@retry(tries=5, delay=60)
def send_report_email(run_report_date):
    """Creates an email report for the successful upis for the previous day"""
    subject = ('Littlewood\'s Gift Wrapping Requests processed on {}'
               .format(run_report_date.strftime("%B %d")))
    report_datetime = datetime.combine(
        run_report_date, time.max).replace(tzinfo=timezone(settings.TIME_ZONE))
    successful_upis_yesterday = _get_success_upis_for_day(run_report_date)
    successful_upis_until_yesterday = _get_success_upis_until_date(
        report_datetime)
    request_count_yesterday = _request_count_for_day(run_report_date)
    request_count_until_yesterday = _request_count_until_date(report_datetime)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipients = settings.UPI_REPORT_RECIPIENTS

    message = _build_message(
        successful_upis_yesterday,
        successful_upis_until_yesterday,
        request_count_yesterday,
        request_count_until_yesterday,
        run_report_date
    )
    html_msg = "<body>" + message.replace("\r\n", "<br>") + "</body>"
    msg = EmailMultiAlternatives(subject, message, from_email, recipients)
    msg.attach_alternative(html_msg, "text/html")
    msg.send()
