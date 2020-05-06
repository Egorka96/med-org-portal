from django.conf import settings


def base_templates(request):
    base_template = settings.TEMPLATES_DICT.get("base") if hasattr(settings, "TEMPLATES_DICT") else 'core/base.html'

    return {
        'BASE_TEMPLATE': base_template
    }


def brand(request):
    return {'BRAND': settings.BRAND}
