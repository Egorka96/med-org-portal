import os
import shutil
import tempfile
from typing import Optional, List, Dict

from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin as DjangoFormMixin
from docxtpl import DocxTemplate, InlineImage
from swutils.string import transliterate

from mis.service_client import Mis


class RestPaginator(Paginator):
    def __init__(self, object_list, per_page, count, *arg, **kwargs):
        super().__init__(object_list, per_page, *arg, **kwargs)
        self._count = count

    @cached_property
    def count(self):
        return self._count


class RestListMixin:
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
            if form.is_valid() or (not form.is_bound and filter_params):
                response_data = Mis().get_response(
                    path=self.mis_request_path,
                    request=self.request,
                    params=filter_params,
                )
                self.object_list = response_data['results']
                self.count = response_data['count']
                self.have_next = bool(response_data['next'])
                self.have_previous = bool(response_data['previous'])
            else:
                self.object_list = []
                self.count = 0

        return self.object_list

    def get_context_data(self, **kwargs):
        self.get_objects()
        c = super().get_context_data(**kwargs)

        user_orgs = self.request.user.core.get_orgs()
        c['show_orgs'] = False if user_orgs and len(user_orgs) < 2 else True

        if self.object_list:
            c['object_list'] = self.object_list

        return c


class FormMixin(DjangoFormMixin):
    data_method = None

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        kwargs.update({
            'data': getattr(self.request, self.data_method.upper() if self.data_method else 'GET') or None,
            'files': self.request.FILES or None
        })
        return kwargs


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
    excel_params = ['excel']

    def get_workbook_maker(self):
        return self.excel_workbook_maker

    def get_excel(self) -> HttpResponse:
        maker = self.get_workbook_maker()
        workbook_maker_kwargs = self.get_workbook_maker_kwargs()

        maker_instance = maker(**workbook_maker_kwargs)
        excel_response = maker_instance.create_workbook()
        return excel_response

    def get_workbook_maker_kwargs(self, **kwargs):
        kwargs.update({
            'objects': self.get_queryset(),
            'title': self.get_excel_title(),
            'page': self.request.GET.get('page')
        })

        return kwargs

    def get_excel_title(self):
        return self.get_title()

    def get_excel_name(self):
        return self.excel_name or self.get_title()

    def get_excel_method(self):
        return self.excel_method

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

            docx.render(context)
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