import dataclasses
import datetime
import json
import os
import tempfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files import File
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View
from docx.shared import Mm

from mis.direction import Direction
from mis.service_client import Mis

import core.generic.mixins
import core.generic.views
import core.datatools.barcode

from core import forms, models


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
             core.generic.views.ListView):
    form_class = forms.DirectionSearch
    title = 'Направления'
    permission_required = 'core.view_direction'
    paginate_by = 50
    template_name = settings.TEMPLATES_DICT.get("direction_list")
    mis_request_path = Mis.DIRECTIONS_LIST_URL

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def get_initial(self):
        initial = super().get_initial()
        initial['date_from'] = datetime.date.today()
        return initial

    def get_filter_params(self):
        return dict(self.request.GET) or self.get_initial()


class Edit(PermissionRequiredMixin, core.generic.views.EditView):
    template_name = 'core/directions/edit.html'
    form_class = forms.DirectionEdit
    data_method = 'post'
    pk_url_kwarg = 'number'

    def has_permission(self):
        perms = self.get_permission_required()
        return any([self.request.user.has_perm(perm) for perm in perms])

    def get_permission_required(self):
        permission_required = [self.get_edit_permission()]
        if self.request.method == 'GET' and self.kwargs.get(self.pk_url_kwarg):
            permission_required.append('core.view_direction')

        return permission_required

    def get_edit_permission(self):
        if self.kwargs.get(self.pk_url_kwarg):
            return 'core.change_direction'
        else:
            return 'core.add_direction'

    def get_success_url(self):
        return reverse_lazy('core:direction_list')

    def get_initial(self):
        initial = super().get_initial()
        obj = self.get_object()
        if obj:
            initial.update(dataclasses.asdict(obj))
            if initial.get('org'):
                initial['org'] = initial['org']['id']

            if initial.get('law_items_section_1'):
                initial['law_items_section_1'] = [l_i['id'] for l_i in initial['law_items_section_1']]

            if initial.get('law_items_section_2'):
                initial['law_items_section_2'] = [l_i['id'] for l_i in initial['law_items_section_2']]

            if initial.get('pay_method'):
                initial['pay_method'] = initial['pay_method']['id']

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def get_object(self):
        object_pk = self.kwargs.get(self.pk_url_kwarg)
        if object_pk:
            self.object = Direction.get(direction_id=object_pk)

        return self.object

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj and obj.confirm_date:
            messages.error(self.request, 'Редактирование направления запрещено: '
                                         'по нему уже создана заявка на осмотр в медицинской информационной системе')
            return super().get(request, *args, **kwargs)

        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        if self.kwargs.get(self.pk_url_kwarg):
            success, description = Direction.edit(direction_id=self.kwargs[self.pk_url_kwarg], params=form.cleaned_data)
        else:
            success, description = Direction.create(params=form.cleaned_data)

        if success:
            messages.success(self.request, description)
        else:
            messages.error(self.request, description)
            return self.form_invalid(form)

        return redirect(self.get_success_url())

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            ('Направления', reverse('core:direction_list')),
            (self.get_title(), ''),
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_edit'] = True
        if not self.request.user.has_perm(self.get_edit_permission()):
            context['can_edit'] = False

        obj = self.get_object()
        if obj and obj.confirm_date:
            context['can_edit'] = False
            messages.warning(self.request, 'Редактирование направления запрещено: '
                                           'по нему уже создана заявка на осмотр в медицинской информационной системе')

        return context


class Delete(PermissionRequiredMixin, core.generic.views.DeleteView):
    success_url = reverse_lazy('core:direction_list')
    breadcrumb = 'Удалить'
    permission_required = 'core.delete_direction'
    pk_url_kwarg = 'number'

    def get_object(self, *args, **kwargs):
        if self.object is None:
            object_pk = self.kwargs.get(self.pk_url_kwarg)
            self.object = Direction.get(direction_id=object_pk)
        return self.object

    def get_breadcrumbs(self):
        direction = self.get_object()
        return [
            ('Главная', reverse('core:index')),
            ('Направления', reverse('core:direction_list')),
            (direction, reverse('core:direction_edit', kwargs={'number': direction.number})),
            (self.breadcrumb, ''),
        ]

    def delete(self, *args, **kwargs):
        success, description = Direction.delete(direction_id=self.kwargs.get(self.pk_url_kwarg))

        if success:
            messages.success(self.request, description)
        else:
            messages.error(self.request, description)
            return self.render_to_response(self.get_context_data())

        return redirect(self.success_url)


class Print(PermissionRequiredMixin, core.generic.mixins.DocxMixin, View):
    permission_required = 'core.view_direction'
    print_message = 'Печать направления'
    pk_url_kwarg = 'number'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = None

    def get_file_name(self):
        return str(self.get_object())

    def get_print_template(self):
        obj = self.get_object()

        docx_template_file = None
        docx_templates = models.DirectionDocxTemplate.objects.exclude(org_ids='')
        for template in docx_templates:
            if obj.org.id in json.loads(template.org_ids):
                docx_template_file = template.file.path
                break

        if not docx_template_file:
            docx_template = models.DirectionDocxTemplate.objects.filter(org_ids='').first()
            if not docx_template:
                docx_template = models.DirectionDocxTemplate.objects.create(
                    name='Основной шаблон',
                )
                with open(os.path.join(settings.BASE_DIR, 'core/templates/core/directions/print.docx'), 'rb') as f:
                    docx_template.file.save(
                        name='direction_print.docx',
                        content=File(f)
                    )
            docx_template_file = docx_template.file.path

        return docx_template_file

    def get_object(self, *args, **kwargs):
        if self.object is None:
            object_pk = self.kwargs.get(self.pk_url_kwarg)
            self.object = Direction.get(direction_id=object_pk)
        return self.object

    def get_print_context_data(self, **kwargs):
        context = super().get_print_context_data(**kwargs)
        context['object'] = self.get_object()
        context['user'] = self.request.user

        # добавим штрих-код заявки
        direction_barcode_path = core.datatools.barcode.create_jpg(
            context['object'].number,
            tmp_dir=tempfile.mkdtemp(dir=settings.DIR_FOR_TMP_FILES),
            module_height=5,
            write_text=False
        )
        context['images'] = {
            'direction_barcode': core.generic.mixins.DocxImage(
                direction_barcode_path, width=Mm(40), height=Mm(15)
            )
        }
        return context
