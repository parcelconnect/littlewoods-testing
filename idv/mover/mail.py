from django.conf import settings

from idv.collector.models import Credential
from idv.common.mail import create_mail

from .reporting import report_csv


def send_move_report(date_range, recipients=None):
    """
    Sends report regarding the credentials that have been uploaded/moved on
    `date`.

    Args:
        date (datetime.date): Date to generate report for
        recipients (list of strings): Who to send the report to
    """
    subject = _get_move_report_subject(date_range)
    context = _get_move_report_context(date_range)
    recipients = recipients or settings.REPORT_RECIPIENTS

    msg = create_mail(
        subject=subject,
        template_prefix='move_report',
        emails=recipients,
        context=context,
        app_name='mover'
    )

    with report_csv(date_range) as report:
        report_content = report.getvalue()
    report_filename = _get_move_report_filename(date_range)

    msg.attach(report_filename, report_content, 'text/csv')
    msg.send()


def _get_move_report_subject(date_range):
    since, until = date_range
    n_days = (until - since).days
    date_fmt = "%Y-%m-%d"
    if n_days == 1:
        period = since.strftime(date_fmt)
    else:
        period = "{since} - {until} (excluded)".format(
            since=since.strftime(date_fmt),
            until=until.strftime(date_fmt),
        )
    return "Littlewoods ID&V Report for {period}".format(period=period)


def _get_move_report_filename(date_range):
    since, until = date_range
    n_days = (until - since).days
    date_fmt = "%Y%m%d"
    if n_days == 1:
        period = since.strftime(date_fmt)
    else:
        period = "{since}-{until}_excluded".format(
            since=since.strftime(date_fmt),
            until=until.strftime(date_fmt),
        )
    return "idv_report_{period}.csv".format(period=period)


def _get_move_report_context(date_range):
    creds_qs = Credential.objects.created_between(date_range)
    moved = creds_qs.moved()
    not_found = creds_qs.not_found()
    return {
        'n_moved': moved.count(),
        'n_not_found': not_found.count(),
    }
