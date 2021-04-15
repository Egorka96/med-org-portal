import dataclasses

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View
from swutils.string import transliterate
from django.contrib import messages
from django.shortcuts import redirect

import core.generic.mixins
import core.generic.views

from core import forms, filters, models
from mis.document import Document
from mis.service_client import Mis
from mis.worker import Worker


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

    def process_response_results(self, objects):
        return [Worker.get_from_dict(obj) for obj in objects]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_orgs = self.request.user.core.get_orgs()
        context['show_orgs'] = False if user_orgs and len(user_orgs) < 2 else True

        return context

class DocumentPrint(PermissionRequiredMixin, View):
    permission_required = 'core.view_worker'

    def get(self, request, *args, **kwargs):
        worker_id = self.request.GET.get('worker_id')
        document_link = self.request.GET.get('document_link')

        if not worker_id:
            return HttpResponse("Не указан сотрудник, по которому необходимо печатать документ.")

        worker = models.Worker.objects.get(id=worker_id)
        file_name = transliterate(str(worker))
        pdf_content = Document.get_content(path=document_link)

        # сгенерируем HttpResponse-объект с pdf
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response['Content-Disposition'] = 'filename=%s.pdf' % file_name
        return response


class Edit(PermissionRequiredMixin, core.generic.views.EditView):
    model = models.Worker
    template_name = 'core/workers/edit.html'
    permission_required = 'core.view_worker'
    data_method = 'post'
    form_class = forms.WorkerEdit

    def has_permission(self):
        perms = self.get_permission_required()
        return any([self.request.user.has_perm(perm) for perm in perms])

    def get_permission_required(self):
        permission_required = [self.get_edit_permission()]
        if self.request.method == 'GET' and self.kwargs.get(self.pk_url_kwarg):
            permission_required.append('core.view_worker')

        return permission_required

    def get_edit_permission(self):
        if self.kwargs.get(self.pk_url_kwarg):
            return 'core.change_worker'
        else:
            return 'core.add_worker'

    def get_success_url(self):
        return reverse_lazy('core:workers')

    def form_valid(self, form):
        worker = form.save()
        worker_org = {
            'org_id': form.cleaned_data['org'],
            'post': form.cleaned_data['post'],
            'shop': form.cleaned_data['shop'],
            'start_work_date': form.cleaned_data['start_work_date'],
            'end_work_date': form.cleaned_data['end_work_date']
        }
        if self.kwargs.get(self.pk_url_kwarg):
            worker_mis = models.WorkerOrganization.objects.get(worker=self.kwargs[self.pk_url_kwarg])
            success, description, worker_data = Worker.edit(worker_mis.mis_id, params=form.cleaned_data)
            models.WorkerOrganization.objects.filter(worker=worker_mis.worker).update(
                **worker_org
            )
        else:
            success, description, worker_data = Worker.create(params=form.cleaned_data)
            models.WorkerOrganization.objects.create(
                worker=worker,
                mis_id=worker_data['id'],
                **worker_org
            )

        if success:
            messages.success(self.request, description)
        else:
            messages.error(self.request, description)
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_initial(self):
        initial = super().get_initial()
        obj = self.get_object()
        if obj:
            worker_org = models.WorkerOrganization.objects.get(worker=obj)
            initial['org'] = worker_org.org_id
            initial['post'] = worker_org.post
            initial['shop'] = worker_org.shop
            initial['start_work_date'] = worker_org.start_work_date
            initial['end_work_date'] = worker_org.end_work_date

            worker_mis = Worker.get(worker_org.mis_id)
            if worker_mis.law_items:
                for l_i in worker_mis.law_items:
                    field_name = f'law_items_{l_i.law.name.replace("н", "")}'
                    if l_i.law.name == '302н':
                        field_name += f'_section_{l_i.section}'

                    initial.setdefault(field_name, []).append(l_i.id)

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = True
        if not self.request.user.has_perm(self.get_edit_permission()):
            context['can_edit'] = False

        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs


class Delete(PermissionRequiredMixin, core.generic.views.DeleteView):
    success_url = reverse_lazy('core:workers')
    breadcrumb = 'Удалить'
    permission_required = 'core.delete_worker'
    model = models.Worker

    def delete(self, *args, **kwargs):
        pk_url_kwarg = self.kwargs.get(self.pk_url_kwarg)
        workers_mis = models.WorkerOrganization.objects.filter(worker=pk_url_kwarg)

        for worker_mis in workers_mis:
            success, description = Worker.delete(worker_id=worker_mis.mis_id)

            if not success:
                messages.error(self.request, description)
                return self.render_to_response(self.get_context_data())

        models.Worker.objects.filter(id=pk_url_kwarg).delete()

        return redirect(self.success_url)
