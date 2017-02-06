from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from idv.common.decorators import retry
from idv.giftwrap.models import GiftWrapRequest


def _get_success_upis_for_day(date):
    return (
        GiftWrapRequest.objects
        .modified_on(date)
        .success()
        .values_list("upi", flat=True)
    )


def _get_request_upis_for_day(date):
    return (
        GiftWrapRequest.objects
        .created_on(date)
        .values_list("upi", flat=True)
    )


def _get_request_upis_until_date(date):
    return (
        GiftWrapRequest.objects
        .created_until(date)
        .values_list("upi", flat=True)
    )


def _get_success_upis_until_date(date):
    return (
        GiftWrapRequest.objects
        .modified_until(date)
        .success()
        .values_list("upi", flat=True)
    )


def _build_message(successful_yesterday, successful_until_yesterday,
                   requests_yesterday, requests_until_yesterday, date):
    message = ""
    message = message + (
        "There were {} successful gift wrapping requests processed on {}."
        "\r\n".format(len(successful_yesterday), date)
    )

    for upi in successful_yesterday:
        message = message + upi + "\r\n"

    message = message + (
        "-------------------------------------------------\r\n\r\n"
        "There were {} successful gift wrapping requests processed until {}."
        "\r\n".format(len(successful_until_yesterday), date)
    )

    for upi in successful_until_yesterday:
        message = message + upi + "\r\n"

    message = message + (
        "-------------------------------------------------\r\n\r\n"
        "There were {} gift wrapping requests processed on {}."
        "\r\n".format(len(requests_yesterday), date)
    )

    for upi in requests_yesterday:
        message = message + upi + "\r\n"

    message = message + (
        "-------------------------------------------------\r\n\r\n"
        "There were {} gift wrapping requests processed until {}."
        "\r\n".format(len(requests_until_yesterday), date)
    )

    for upi in requests_until_yesterday:
        message = message + upi + "\r\n"

    return message


@retry(tries=5, delay=60)
def send_report_email(run_report_date):
    """
     Creates an email report for the successful upis for the previous day
    """

    formatted_date = run_report_date.strftime("%B %d")
    successful_upis_yesterday = _get_success_upis_for_day(run_report_date)
    successful_upis_until_yesterday = _get_success_upis_until_date(
        run_report_date
    )
    requests_yesterday = _get_request_upis_for_day(run_report_date)
    requests_until_yesterday = _get_request_upis_until_date(run_report_date)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipients = settings.UPI_REPORT_RECIPIENTS
    subject = ('Littlewood\'s Gift Wrapping Requests processed on {}'
               .format(formatted_date))

    message = _build_message(
        successful_upis_yesterday,
        successful_upis_until_yesterday,
        requests_yesterday,
        requests_until_yesterday,
        run_report_date
    )

    msg = EmailMultiAlternatives(subject, message, from_email, recipients)
    msg.send()
