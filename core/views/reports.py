from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse

import core.generic.mixins
import core.generic.views

from core import forms
from core.datatools.report import get_report_period
from core.excel.reports import WorkersDoneExcel
from core.mis.service_client import Mis


class WorkersDoneReport(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
                        core.generic.views.ListView):
    template_name = 'core/reports/workers_done.html'
    title = 'Отчет по прошедшим'
    form_class = forms.WorkersPastReport
    paginate_by = 50
    permission_required = 'core.view_workers_done_report'
    excel_workbook_maker = WorkersDoneExcel
    mis_request_path = Mis.WORKERS_DONE_REPORT_URL

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

    def get_excel_title(self):
        title = self.get_title()

        form = self.get_form()
        if form.is_valid():
            title += get_report_period(
                date_from=form.cleaned_data.get('date_from'),
                date_to=form.cleaned_data.get('date_to')
            )

            if orgs := form.cleaned_data.get('orgs'):
                title += f'. Организации: {", ".join(str(org) for org in orgs)}'

        return title

    def get_filter_params(self):
        filter_params = super().get_filter_params()

        if self.request.GET:
            filter_params['group_clients'] = True
        return filter_params

    def get_objects(self):
        self.object_list = super().get_objects()
        self.object_list = self.update_object_list(self.object_list)
        return self.object_list

    def update_object_list(self, objects):
        for obj in objects:
            obj['main_services'] = []

            for app in ['prof', 'lmk', 'certificate', 'heal']:
                app_orders = obj[app]
                for o in app_orders:
                    obj['main_services'].append(o.get('main_services'))

        return objects
