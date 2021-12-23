from django.conf import settings
from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin


class Management(PermissionRequiredMixin, TemplateView):
    template_name = 'core/admin.html'
    permission_required = 'core.view_management'