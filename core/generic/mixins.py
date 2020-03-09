from django.core.paginator import Paginator
from django.utils.functional import cached_property
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormMixin as DjangoFormMixin


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
