import core.generic.mixins
import core.generic.views
from django.contrib.auth.mixins import PermissionRequiredMixin

from core import models, forms, filters


class Log(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.views.ListView):
    template_name = 'core/log.html'
    model = models.Log
    form_class = forms.Log
    filter_class = filters.Log
    title = 'Журнал'
    permission_required = 'core.view_log'