import contextlib
import csv
import io

from django.contrib.postgres.aggregates import ArrayAgg

from idv.collector.models import Account, Credential


def get_report_data(date_range):
    cred_qs = Credential.objects.created_between(date_range)
    cred_qs = cred_qs.values_list('account__pk')

    moved = cred_qs.moved().annotate(s3_keys=ArrayAgg('s3_key'))
    # {account pk: ['moved1.jpg', 'move2.png'], ...}
    moved = dict(moved)

    not_found = cred_qs.not_found().annotate(s3_keys=ArrayAgg('s3_key'))
    # {account pk: ['not_found1.jpg', 'not_found.png'], ...}
    not_found = dict(not_found)

    account_pks = set(list(moved.keys()) + list(not_found.keys()))
    accounts = Account.objects.filter(pk__in=account_pks)

    data = [
        {
            'account_number': account.account_number,
            'email': account.email,
            'files_moved': moved.get(account.pk, []),
            'files_not_found': not_found.get(account.pk, []),
        }
        for account in accounts
    ]
    return data


def generate_report_csv_content(date_range):
    data = get_report_data(date_range)

    csv_headers = ['account_number', 'email', 'files_moved', 'files_not_found']
    csv_rows = [csv_headers]

    for account_data in data:
        csv_rows.append([
            account_data['account_number'],
            account_data['email'],
            ','.join(account_data['files_moved']),
            ','.join(account_data['files_not_found']),
        ])
    return csv_rows


@contextlib.contextmanager
def report_csv(date_range):
    csv_rows = generate_report_csv_content(date_range)

    with io.StringIO() as csv_fd:
        writer = csv.writer(csv_fd, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerows(csv_rows)
        yield csv_fd
