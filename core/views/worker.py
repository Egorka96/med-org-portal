from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse

import core.generic.mixins
import core.generic.views

from core import forms
from mis.service_client import Mis
from mis.worker import Worker


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
             core.generic.views.ListView):
    title = 'Сотрудники'
    form_class = forms.WorkerSearch
    paginate_by = 100
    permission_required = 'core.view_worker'
    template_name = 'core/workers/list.html'
    mis_request_path = Mis.WORKERS_LIST_URL
    load_without_params = True

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def process_response_results(self, objects):
        return [Worker.get_from_dict(obj) for obj in objects]
