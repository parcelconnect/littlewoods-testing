from django.conf import settings

from idv.collector.models import Credential
from idv.common.mail import create_mail

from .reporting import report_csv


def send_daily_report(date, recipients=None):
    """
    Sends report regarding the credentials that have been uploaded/moved on
    `date`.

    Args:
        date (datetime.date): Date to generate report for
        recipients (list of strings): Who to send the report to
    """
    date_str = date.strftime("%Y-%m-%d")

    subject = "Daily Littlewoods ID&V Report for {}".format(date_str)
    context = _get_daily_report_context(date)
    recipients = recipients or settings.REPORT_RECIPIENTS

    msg = create_mail(
        subject=subject,
        template_prefix='daily_report',
        emails=recipients,
        context=context,
        app_name='mover'
    )

    with report_csv(date) as report:
        report_content = report.getvalue()
    report_filename = 'idv_report_{}.csv'.format(date_str)

    msg.attach(report_filename, report_content, 'text/csv')
    msg.send()


def _get_daily_report_context(date):
    n_moved = Credential.objects.moved_on(date).count()
    n_not_found = Credential.objects.created_on(date).not_found()
    return {
        'n_moved': n_moved,
        'n_not_found': n_not_found
    }
