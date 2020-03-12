from swutils.date import date_to_rus


def get_report_period(date_from=None, date_to=None):
    period = ''
    if date_from or date_to:
        if date_from == date_to:
            period = ' за период ' + date_to_rus(date_from)
        elif date_from and date_to:
            period = ' за период с ' + date_to_rus(date_from) + ' по ' + date_to_rus(date_to)
        else:
            if date_from:
                period = ' за период с ' + date_to_rus(date_from)
            else:
                period = ' за период по ' + date_to_rus(date_to)
    return period
