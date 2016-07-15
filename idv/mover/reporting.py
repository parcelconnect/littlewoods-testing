import contextlib
import csv
import io
import itertools

from django.contrib.postgres.aggregates import ArrayAgg

from idv.collector.models import Account, Credential


def generate_report_csv_content(date_range):
    credentials_qs = Credential.objects.values('account__pk')
    credentials_qs = credentials_qs.created_between(date_range)

    moved = credentials_qs.moved()
    moved = moved.annotate(moved=ArrayAgg('s3_key'))

    not_found = credentials_qs.not_found()
    not_found = not_found.annotate(not_found=ArrayAgg('s3_key'))

    account_pks = [
        group['account__pk'] for group in itertools.chain(moved, not_found)
    ]
    accounts = Account.objects.filter(pk__in=account_pks)
    accounts = {account.pk: account for account in accounts}

    csv_headers = ['account_number', 'email', 'files_moved', 'files_not_found']
    csv_rows = [csv_headers]

    for group in itertools.chain(moved, not_found):
        account_pk = group['account__pk']
        account = accounts[account_pk]
        files_moved = group.get('moved', [])
        files_not_found = group.get('not_found', [])

        csv_rows.append([
            account.account_number,
            account.email,
            ','.join(files_moved),
            ','.join(files_not_found)
        ])
    return csv_rows


@contextlib.contextmanager
def report_csv(date_range):
    csv_rows = generate_report_csv_content(date_range)

    with io.StringIO() as csv_fd:
        writer = csv.writer(csv_fd, delimiter=',', quoting=csv.QUOTE_ALL)
        writer.writerows(csv_rows)
        yield csv_fd
