from typing import Optional, List, Dict

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse

import core.generic.mixins
import core.generic.views

from core import forms


class WorkersDoneReport(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.views.ListView):
    template_name = 'core/reports/workers_done.html'
    title = 'Отчет по прошедшим'
    form_class = forms.WorkersPastReport
    paginate_by = 50
    permission_required = 'core.view_workers_done_report'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_list: Optional[List[Dict]] = None

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def get_queryset(self):
        if self.get_objects() is None:
            return []
        else:
            return self.get_objects()

    def get_objects(self):
        return   # todo
