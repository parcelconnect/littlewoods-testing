from django.conf import settings

from idv.collector.models import Credential
from idv.common.mail import create_mail

from .reporting import report_csv


def send_daily_report(date_range, recipients=None):
    """
    Sends report regarding the credentials that have been uploaded/moved on
    `date`.

    Args:
        date (datetime.date): Date to generate report for
        recipients (list of strings): Who to send the report to
    """
    date_str = date_range[0].strftime("%Y-%m-%d")

    subject = "Daily Littlewoods ID&V Report for {}".format(date_str)
    context = _get_daily_report_context(date_range)
    recipients = recipients or settings.REPORT_RECIPIENTS

    msg = create_mail(
        subject=subject,
        template_prefix='daily_report',
        emails=recipients,
        context=context,
        app_name='mover'
    )

    with report_csv(date_range) as report:
        report_content = report.getvalue()
    report_filename = 'idv_report_{}.csv'.format(date_str)

    msg.attach(report_filename, report_content, 'text/csv')
    msg.send()


def _get_daily_report_context(date_range):
    creds_qs = Credential.objects.created_between(date_range)
    moved = creds_qs.moved()
    not_found = creds_qs.not_found()
    return {
        'n_moved': moved.count(),
        'n_not_found': not_found.count(),
    }
