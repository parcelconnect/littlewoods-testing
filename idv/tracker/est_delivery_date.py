from datetime import datetime, timedelta

BANK_HOLIDAYS = (
    datetime(year=2017, month=10, day=31),
    datetime(year=2017, month=12, day=25),
    datetime(year=2017, month=12, day=26),
    datetime(year=2017, month=12, day=27),
    datetime(year=2018, month=1, day=2),
    datetime(year=2018, month=3, day=17),
    datetime(year=2018, month=4, day=2),
    datetime(year=2018, month=5, day=1),
    datetime(year=2018, month=6, day=5),
    datetime(year=2018, month=8, day=6),
    datetime(year=2018, month=10, day=29),
    datetime(year=2018, month=12, day=25),
    datetime(year=2018, month=12, day=26),
)

PLUS_1_DAY_SCANS = [
    "U01", "U02", "U03", "U04", "U05", "U06", "U07", "U08",
    "U09", "U10", "U11", "U12", "U13", "U14", "U15", "U16", "U17", "U18",
    "U19", "U20", "U21", "U22", "U23", "U24", "U25", "U26", "U27", "U28",
    "U29", "U30", "U31", "U32", "U33", "U34", "U35", "U36", "U37", "U38",
    "U39", "U40", "U41", "U42", "U43", "U44", "U45", "U46", "U47", "U48",
    "DS1", "R10"]

PLUS_2_DAYS_SCANS = ["R02", "RTD"]

SAME_DAY_SCANS = ["HDN", "ONB"]


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
    return delivery_date.strftime('%B %d, %Y')


def get_est_delivery_date_from_event(event):
    status_scan = event['status_scan']
    if status_scan in SAME_DAY_SCANS:
        return event['date']
    elif status_scan in PLUS_1_DAY_SCANS:
        return _get_week_day(start_date=event['date'], plus_days=1)
    elif status_scan in PLUS_2_DAYS_SCANS:
        return _get_week_day(start_date=event['date'], plus_days=2)
    # default estimated delivery is +2 days, this is subject to change
    else:
        return _get_week_day(start_date=event['date'], plus_days=2)
