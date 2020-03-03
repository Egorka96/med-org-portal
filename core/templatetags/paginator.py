from urllib.parse import urlencode

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def params_with_page(context, page_number):
    query_string = '?'
    get_params = dict(context['request'].GET)
    get_params['page'] = [str(page_number)]

    for key, params in get_params.items():
        if hasattr(params, '__iter__'):
            for param in params:
                query_string += f'{key}={param}&'
        else:
            query_string += f'{key}={param}&'

    return query_string


@register.simple_tag(takes_context=True)
def set_per_page(context, count, additional_params=None):
    request = context['request']
    path = request.path
    params = dict(request.GET)
    params['per_page'] = count
    additional_params = dict(additional_params)
    if 'per_page' in additional_params:
        del additional_params['per_page']
    params.update(additional_params or {})

    if 'page' in params:
        del params['page']

    return '{0}?{1}'.format(path, urlencode(params, doseq=True))

