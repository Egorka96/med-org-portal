import pprint

from django import template

import swutils.date
from swutils.string import transliterate as transliterate_value

from core.datatools.date import get_month_rus_genitive, get_month_rus

register = template.Library()


def get_jinja_filters():
    """
    Словарь c фильтрами для jinja
    """
    return {
        'month_in_nominative': month_in_nominative,
        'month_in_genitive': month_in_genitive,
        'transliterate': transliterate,
        'rus_to_date': rus_to_date,
        'date_to_rus': date_to_rus,
    }


@register.filter()
def month_in_nominative(date):
    month = None
    if date:
        try:
            month = int(date) if isinstance(date, str) else date.month
        except ValueError:
            pass
    return get_month_rus(month) or date


@register.filter()
def month_in_genitive(date):
    month = None
    if date:
        try:
            month = int(date) if isinstance(date, str) else date.month
        except ValueError:
            pass
    return get_month_rus_genitive(month) or date


@register.filter()
def transliterate(value):
    return transliterate_value(value)


@register.filter()
def date_to_rus(value):
    return swutils.date.date_to_rus(value)


@register.filter()
def rus_to_date(value):
    return swutils.date.rus_to_date(value)


@register.filter()
def pretty_value(value):
    return pprint.pformat(value, indent=2)
