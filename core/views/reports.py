import json
from typing import Optional, List, Dict

import requests
from django.conf import settings
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse

import core.generic.mixins
import core.generic.views

from core import forms
from core.excel.reports import WorkersDoneExcel


class WorkersDoneReport(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
                        core.generic.views.ListView):
    template_name = 'core/reports/workers_done.html'
    title = 'Отчет по прошедшим'
    form_class = forms.WorkersPastReport
    paginate_by = 50
    permission_required = 'core.view_workers_done_report'
    excel_workbook_maker = WorkersDoneExcel

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_list: Optional[List[Dict]] = None

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def get_workbook_maker_kwargs(self, **kwargs):
        kwargs = super().get_workbook_maker_kwargs(**kwargs)

        user_orgs = self.request.user.core.get_orgs()
        kwargs['show_orgs'] = False if user_orgs and len(user_orgs) < 2 else True
        return kwargs

    def get_queryset(self):
        if self.get_objects() is None:
            return []
        else:
            return self.get_objects()

    def get_objects(self):
        if self.object_list is None:
            form = self.get_form()
            if form.is_valid():
                filter_params = dict(self.request.GET)

                if self.request.user.core.org_ids and not filter_params.get('orgs'):
                    filter_params.update({
                        'orgs': json.loads(self.request.user.core.org_ids)
                    })

                url = settings.MIS_URL + '/api/orders/by_client_date/'

                if filter_params.get('per_page'):
                    url += f"?per_page={filter_params['per_page'][0]}"

                headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

                response = requests.post(url=url, data=filter_params, headers=headers)
                response.raise_for_status()

                response_data = response.json()
                self.object_list = self.update_object_list(response_data['results'])
                self.count = response_data['count']
                self.have_next = bool(response_data['next'])
                self.have_previous = bool(response_data['previous'])
            else:
                self.object_list = []
                self.count = 0

        return self.object_list

    def update_object_list(self, objects):
        for obj in objects:
            obj['main_services'] = []

            for app in ['prof', 'lmk', 'certificate', 'heal']:
                app_orders = obj[app]
                for o in app_orders:
                    obj['main_services'].append(o.get('main_services'))

        return objects

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)

        user_orgs = self.request.user.core.get_orgs()
        c['show_orgs'] = False if user_orgs and len(user_orgs) < 2 else True
        return c
