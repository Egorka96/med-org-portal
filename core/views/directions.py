from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse

import core.generic.mixins
import core.generic.views

from core import forms
from core.mis.service_client import Mis


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
             core.generic.views.ListView):
    template_name = 'core/directions/list.html'
    form_class = forms.DirectionSearch
    title = 'Направления'
    permission_required = 'core.view_direction'
    paginate_by = 50
    mis_request_path = Mis.DIRECTIONS_LIST_URL

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]
