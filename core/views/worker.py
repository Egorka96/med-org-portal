from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic.base import View
from swutils.string import transliterate

import core.generic.mixins
import core.generic.views

from core import forms, filters, models
from mis.document import Document


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.views.ListView):
    title = 'Сотрудники'
    model = models.Worker
    form_class = forms.WorkerSearch
    paginate_by = 100
    permission_required = 'core.view_worker'
    template_name = 'core/workers/list.html'
    filter_class = filters.Worker
    load_without_params = True

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_orgs = self.request.user.core.get_orgs()
        context['show_orgs'] = False if user_orgs and len(user_orgs) < 2 else True

        return context
