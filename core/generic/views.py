import sys
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import (
    ListView as DjangoListView,
    UpdateView as DjangoUpdateView,
    DeleteView as DjangoDeleteView,
)

from core.generic import mixins


class ListView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoListView):
    DEFAULT_PAGINATE_BY = 50

    def get_paginate_by(self, queryset=None):
        paginate_by = self.request.session.get(f'per_page-{self.request.path}',
                                               self.paginate_by or self.DEFAULT_PAGINATE_BY)
        per_page = self.request.GET.get('per_page')
        if per_page:
            self.request.session[f'per_page-{self.request.path}'] = per_page
            paginate_by = per_page

        return paginate_by if paginate_by != 'all' else sys.maxsize

    def get_page_numbers(self, queryset=None):

        if queryset is None:
            queryset = self.get_queryset()

        numbers = []
        if queryset:
            page = int(self.request.GET.get('page', 1))
            per_page = self.get_paginate_by(queryset)

            pag = self.get_paginator(queryset, per_page or len(queryset))
            all_numbers = list(pag.page_range)

            start = page - 4 if page - 4 > 1 else 0
            end = page + 3
            numbers = all_numbers[start:end]

        has_left = False
        has_right = False
        if numbers:
            has_left = numbers[0] != all_numbers[0]
            has_right = numbers[-1] != all_numbers[-1]

        return has_left, numbers, has_right

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = None
        if hasattr(self, 'object_list'):
            queryset = self.object_list

        has_left, numbers, has_right = self.get_page_numbers(queryset=queryset)
        context['page_has_left'] = has_left
        context['page_numbers'] = numbers
        context['page_has_right'] = has_right
        return context

    def get_queryset(self):
        queryset = self.model.objects.all()
        form = self.get_form()

        if form.is_valid():
            queryset = self.filter_class(
                data=self.request.GET,
                queryset=queryset,
                request=self.request,
            ).qs
        return queryset.distinct()


class EditView(mixins.BreadcrumbsMixin, mixins.TitleMixin, mixins.FormMixin, DjangoUpdateView):
    object = None

    def get_object(self):
        object_pk = self.kwargs.get(self.pk_url_kwarg)
        if object_pk:
            self.object = get_object_or_404(self.model, pk=object_pk)

        return self.object

    def get_title(self):
        if obj := self.get_object():
            return str(obj)
        else:
            return 'Создание'

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())


class DeleteView(mixins.BreadcrumbsMixin, mixins.TitleMixin, DjangoDeleteView):
    object = None
    delete_message = None
    template_name = 'core/base_delete.html'

    def get_delete_message(self):
        return self.delete_message or str(self.object)

    def get_object(self, queryset=None):
        if not self.object:
            self.object = super().get_object(queryset=queryset)

        return self.object

    def get_title(self):
        return f'Удаление "{self.get_object()}"'

    def delete(self, *args, **kwargs):
        response = super().delete(*args, **kwargs)

        if self.request.is_ajax():
            response = HttpResponse('ok')

        return response

