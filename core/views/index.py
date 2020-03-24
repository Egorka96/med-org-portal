from django.conf import settings
from django.views.generic import TemplateView


class Index(TemplateView):
    template_name = settings.TEMPLATES_DICT.get("index") if hasattr(settings, "TEMPLATES_DICT") else 'core/index.html'
