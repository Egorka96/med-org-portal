import logging
import os
import shutil
import tempfile
from typing import Optional, List, Dict
from urllib.parse import quote

import jinja2
import sw_logger.consts
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin as DjangoFormMixin
from djutils.views.helpers import url_params
from docxtpl import DocxTemplate, InlineImage
from swutils.string import transliterate

import background_tasks.models

from core.templatetags.custom_tags import get_jinja_filters
from mis.service_client import Mis


logger = logging.getLogger('db')


class RestPaginator(Paginator):
    def __init__(self, object_list, per_page, count, *arg, **kwargs):
        super().__init__(object_list, per_page, *arg, **kwargs)
        self._count = count

    @cached_property
    def count(self):
        return self._count


class RestListMixin:
    load_without_params = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_list: Optional[List[Dict]] = None
        self.count = None
        self.have_next = None
        self.have_previous = None

    def get_paginator(self, queryset, per_page, **kwargs):
        return RestPaginator(queryset, per_page, self.count or 0)

    def get_page_numbers(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        numbers = []
        if queryset:
            page = int(self.request.GET.get('page', 1))
            per_page = self.get_paginate_by(queryset)

            pag = self.get_paginator(queryset, per_page)
            all_numbers = list(pag.page_range)

            start = page - 4 if page - 4 > 1 else 0
            end = page + 3
            numbers = all_numbers[start:end]

        return self.have_previous, numbers, self.have_next

    def get_filter_params(self):
        return dict(self.request.GET)

    def get_queryset(self):
        objects = self.get_objects()
        if objects is None:
            return []
        else:
            return objects

    def get_objects(self):
        if self.object_list is None:
            form = self.get_form()
            filter_params = self.get_filter_params()
            if form.is_valid() or (not form.is_bound and (filter_params or self.load_without_params)):
                request_params = filter_params
                request_params['per_page'] = self.request.GET.get('per_page', self.paginate_by)
                response_data = Mis().request(
                    path=self.mis_request_path,
                    user=self.request.user,
                    params=filter_params,
                )
                self.object_list = self.process_response_results(response_data['results'])
                self.count = response_data['count']
                self.have_next = bool(response_data['next'])
                self.have_previous = bool(response_data['previous'])
            else:
                self.object_list = []
                self.count = 0

        return self.object_list

    def process_response_results(self, objects: List[Dict]) -> List[Dict]:
        return objects

    def get_context_data(self, **kwargs):
        self.get_objects()
        c = super().get_context_data(**kwargs)

        user_orgs = self.request.user.core.get_orgs()
        c['show_orgs'] = False if user_orgs and len(user_orgs) < 2 else True

        if self.object_list:
            c['object_list'] = self.object_list

            # если есть выгрузка в excel и количество объектов больше 50, excel скачиваем в фоне
            if hasattr(self, 'excel_workbook_maker') and self.count > 50:
                c['excel_background'] = True

        return c


class FormMixin(DjangoFormMixin):
    data_method = 'GET'

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
            'data': getattr(self.request, self.data_method.upper()) or None,
            'files': self.request.FILES or None
        }

        return kwargs

    def post(self, request, *args, **kwargs):
        if hasattr(super(), 'post'):
            form = self.get_form()
            if form.is_valid():
                response = self.form_valid(form)
                self.log(form)
                return response
            else:
                return self.form_invalid(form)

    def log(self, form):
        if hasattr(form, 'instance') and hasattr(form.instance, 'LOG_NAME'):
            is_update = self.kwargs.get('pk')
            logger.info(
                self.get_log_message(is_update),
                extra=self.get_log_extra(form, is_update)
            )

    def get_log_message(self, is_update):
        return 'Объект обновлен' if is_update else 'Объект создан'

    def get_log_extra(self, form, is_update):
        return {
            'action': sw_logger.consts.ACTION_UPDATED
                    if is_update else sw_logger.consts.ACTION_CREATED,
            'request': self.request,
            'object': form.instance,
        }


class BreadcrumbsMixin(ContextMixin):

    def get_breadcrumbs(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class TitleMixin(ContextMixin):
    title = None

    def get_title(self):
        return self.title

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context


class ExcelMixin:
    excel_name = None
    excel_method = 'get'
    excel_workbook_maker = None
    excel_params = ['excel', 'excel_background']

    def get_workbook_maker(self):
        return self.excel_workbook_maker

    def get_excel(self) -> HttpResponse:
        maker = self.get_workbook_maker()

        if self.is_excel_delay():
            task_params = {
                'workbook_maker_kwargs': self.get_workbook_maker_kwargs(with_objects=False)
            }

            task = background_tasks.models.Task.create_task(
                method=maker.create_workbook_background,
                name=self.get_excel_title()[:255],
                user=self.request.user,
                params=task_params,
            )

            redirect_url = self.get_excel_delay_redirect_url()
            background_task_url = reverse('background_tasks:task_info', kwargs={'pk': task.id}) + \
                                          f"?next={quote(redirect_url)}"

            messages.info(
                self.request,
                mark_safe(f'Создана <strong>фоновая задача</strong> формирования excel-файла '
                          f'<a class="btn btn-outline-secondary" href="{background_task_url}"><i class="fa fa-eye"></i> '
                          f'Показать</a>')
            )
            return redirect(redirect_url)

        workbook_maker_kwargs = self.get_workbook_maker_kwargs()
        maker_instance = maker(**workbook_maker_kwargs)
        excel_response = maker_instance.create_workbook()
        return excel_response

    def get_workbook_maker_kwargs(self, with_objects=True, **kwargs):
        kwargs['title'] = self.get_excel_title()

        if with_objects:
            kwargs['objects'] = self.get_queryset()

        return kwargs

    def get_excel_title(self):
        return self.get_title()

    def get_excel_name(self):
        return self.excel_name or self.get_title()

    def get_excel_method(self):
        return self.excel_method

    def is_excel_delay(self) -> bool:
        """ Выполнять ли формирование excel в фоне """
        if self.request.GET.get('excel_background'):
            return True

        return False

    def get_excel_delay_redirect_url(self):
        return self.request.path + url_params(self.request, except_params=self.excel_params, as_is=True)

    def get(self, *args, **kwargs):
        if self.get_excel_method().lower() == 'get' and \
                any([excel_param in self.request.GET for excel_param in self.excel_params]):
            return self.get_excel()

        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if self.get_excel_method().lower() == 'post' and \
                any([excel_param in self.request.POST for excel_param in self.excel_params]):
            return self.get_excel()

        return super().post(*args, **kwargs)

    def get_context_data(self, **kwargs):
        if self.get_workbook_maker():
            kwargs['add_excel'] = True

        return super().get_context_data(**kwargs)


class DocxImage:
    def __init__(self, path, width=None, height=None):
        self.path = path
        self.width = width
        self.height = height


class DocxMixin:
    print_template_name = None
    file_name = None
    print_message = 'Распечатан docx-документ'

    def get_print_template(self):
        return self.print_template_name

    def get_file_name(self):
        return self.file_name

    def get_print_context_data(self, **kwargs):
        return {}

    def get_object(self):
        return

    def get_objects(self):
        return []

    def get(self, request, *args, **kwargs):
        return self.printed()

    def printed(self):
        file_name = self.get_file_name()
        file_name = file_name.replace("ъ", '').replace("ь", '').replace('"', '').replace('«', '').replace('»', '')
        file_name = transliterate(file_name, space='_')

        filename = os.path.split('/')[-1].split('.')[0]

        if not os.path.exists(settings.DIR_FOR_TMP_FILES):
            os.makedirs(settings.DIR_FOR_TMP_FILES)
        tmp_path = tempfile.mkdtemp(dir=settings.DIR_FOR_TMP_FILES)
        docx_path = '%s/%s.docx' % (tmp_path, filename)

        try:
            docx = DocxTemplate(self.get_print_template())

            context = self.get_print_context_data(docx_tpl=docx)
            if images := context.get('images'):
                for key, image_params in images.items():
                    context[key] = InlineImage(
                        docx, image_params.path, width=image_params.width, height=image_params.height
                    )

            jinja_env = jinja2.Environment()
            jinja_env.filters.update(get_jinja_filters())

            docx.render(context, jinja_env=jinja_env)
            docx.save(docx_path)

            with open(docx_path, mode='rb') as file:
                # сгенерируем HttpResponse-объект с pdf
                response = HttpResponse(
                    file.read(),
                    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                response['Content-Disposition'] = 'filename=%s.docx' % file_name
                return response
        finally:
            shutil.rmtree(tmp_path)