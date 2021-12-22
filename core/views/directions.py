import dataclasses
import datetime
import json
import logging
import os
import tempfile

from core.excel.directions import DirectionsExcel
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.files import File
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View
import sw_logger.consts
from docx.shared import Mm

from mis.direction import Direction
from mis.org import Org
from mis.service_client import Mis
from core.datatools.report import get_report_period

import core.generic.mixins
import core.generic.views
import core.datatools.barcode

from core import forms, models


logger = logging.getLogger('db')


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
             core.generic.views.ListView):
    form_class = forms.DirectionSearch
    title = 'Направления'
    permission_required = 'core.view_direction'
    paginate_by = 50
    excel_workbook_maker = DirectionsExcel
    template_name = settings.TEMPLATES_DICT.get("direction_list")
    mis_request_path = Mis.DIRECTIONS_LIST_URL

    def get_workbook_maker_kwargs(self, **kwargs):
        kwargs = super().get_workbook_maker_kwargs(**kwargs)

        user_orgs = self.request.user.core.get_orgs()
        kwargs['show_orgs'] = False if user_orgs and len(user_orgs) < 2 else True
        kwargs['mis_request_path'] = self.mis_request_path
        kwargs['filter_params'] = self.get_filter_params()
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

    def get_initial(self):
        initial = super().get_initial()
        initial['date_from'] = datetime.date.today()
        return initial

    def get_filter_params(self):
        form = self.get_form()
        if form.is_valid():
            filter_params = form.cleaned_data
        else:
            filter_params = self.get_initial()

        return filter_params

    def process_response_results(self, objects):
        return [Direction.dict_to_obj(obj) for obj in objects]


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

            if initial.get('law_items'):
                for l_i in initial['law_items']:
                    field_name = f'law_items_{l_i["law"]["name"].replace("н", "")}'
                    if l_i["law"]["name"] == '302н':
                        field_name += f'_section_{l_i["section"]}'

                    initial.setdefault(field_name, []).append(l_i["id"])

            if initial.get('pay_method'):
                initial['pay_method'] = initial['pay_method']['id']

            if initial.get('insurance_policy'):
                initial['insurance_number'] = initial['insurance_policy']['number']

        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_user'] = self.request.user
        return kwargs

    def get_object(self):
        if not getattr(self, 'object', None):
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
        obj_id = self.kwargs.get(self.pk_url_kwarg)
        worker, _ = models.Worker.objects.get_or_create(
            last_name=form.cleaned_data.get('last_name'),
            first_name=form.cleaned_data.get('first_name'),
            middle_name=form.cleaned_data.get('middle_name'),
            birth=form.cleaned_data.get('birth'),
            gender=form.cleaned_data.get('gender'),
        )
        direction_dict = {
            'worker': worker,
            'insurance_policy': form.cleaned_data.get('insurance_number'),
            'org_id': form.cleaned_data.get('org'),
            'post': form.cleaned_data.get('post'),
            'shop': form.cleaned_data.get('shop'),
            'exam_type': form.cleaned_data.get('exam_type'),
            'pay_method': form.cleaned_data.get('pay_method')
        }

        if not obj_id:
            direction_id, description = Direction.create(params=form.cleaned_data)
            models.Direction.objects.create(
                mis_id=direction_id,
                **direction_dict
            )
        else:
            direction_id, description = Direction.edit(
                direction_id=obj_id,
                params=form.cleaned_data
            )
            models.Direction.objects.filter(mis_id=direction_id).update(
                **direction_dict
            )

        list_law_items = []
        for field_name in ('law_items_302_section_1', 'law_items_302_section_2', 'law_items_29'):
            list_law_items.extend(form.cleaned_data.get(field_name, []))

        direction_obj = models.Direction.objects.get(mis_id=direction_id)
        list_law_items_ids = []
        for law_item in list_law_items:
            obj, _ = models.DirectionLawItem.objects.get_or_create(
                direction=direction_obj,
                law_item_mis_id=law_item,
            )
            list_law_items_ids.append(obj.id)
        models.DirectionLawItem.objects\
            .filter(direction=direction_obj)\
            .exclude(id__in=list_law_items_ids)\
            .delete()

        if direction_id:
            messages.success(self.request, description)
            is_update = self.kwargs.get('pk')
            logger.info(
                'Направление обновлено' if is_update else 'Направление создано',
                extra={
                    'action': sw_logger.consts.ACTION_UPDATED
                              if is_update else sw_logger.consts.ACTION_CREATED,
                    'request': self.request,
                    'object_id': direction_id,
                    'object_name': 'direction', #todo: Убраь после добовления модели
                }
            )
        else:
            messages.error(self.request, description)
            return self.form_invalid(form)

        return redirect(self.get_success_url())

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
        pk_url_kwarg = self.kwargs.get(self.pk_url_kwarg)
        success, description = Direction.delete(direction_id=pk_url_kwarg)

        if success:
            messages.success(self.request, description)
        else:
            messages.error(self.request, description)
            return self.render_to_response(self.get_context_data())

        models.Direction.objects.filter(id=pk_url_kwarg).delete()

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
        if context['object'].org:
            context['org'] = Org.get(self.object.org.id)

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
