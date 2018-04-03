from datetime import datetime, timedelta

import holidays

BANK_HOLIDAYS = holidays.Ireland(years=[i for i in range(
    2017, datetime.today().year + 1)])

PLUS_1_DAY_SCANS = [
    "U01", "U02", "U03", "U04", "U05", "U06", "U07", "U08",
    "U09", "U10", "U11", "U12", "U13", "U14", "U15", "U16", "U17", "U18",
    "U19", "U20", "U21", "U22", "U23", "U24", "U25", "U26", "U27", "U28",
    "U29", "U30", "U31", "U32", "U33", "U34", "U35", "U36", "U37", "U38",
    "U39", "U40", "U41", "U42", "U43", "U44", "U45", "U46", "U47", "U48",
    "DS1", "R10"]

PLUS_2_DAYS_SCANS = ["R02", "RTD"]

SAME_DAY_SCANS = ["HDN", "ONB", "NEI", "YES"]


def _get_week_day(start_date, plus_days):
    start_date = datetime.strptime(start_date, '%B %d, %Y')
    end_date = start_date + timedelta(days=plus_days)
    delivery_date = start_date
    while delivery_date < end_date:
        if (
            end_date in BANK_HOLIDAYS or
            datetime.weekday(end_date) in set([5, 6])
        ):
            end_date += timedelta(days=1)
        delivery_date += timedelta(days=1)
    return delivery_date


def get_est_delivery_date_from_event(event):
    if event['status_scan'] in SAME_DAY_SCANS:
        return datetime.strptime(event['date'], '%B %d, %Y')
    elif event['status_scan'] in PLUS_1_DAY_SCANS:
        return _get_week_day(start_date=event['date'], plus_days=1)
    elif event['status_scan'] in PLUS_2_DAYS_SCANS:
        return _get_week_day(start_date=event['date'], plus_days=2)
    # default estimated delivery is +2 days, this is subject to change
    else:
        return _get_week_day(start_date=event['date'], plus_days=2)
