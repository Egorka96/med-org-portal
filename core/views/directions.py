import dataclasses

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy

import core.generic.mixins
import core.generic.views

from core import forms
from core.mis.direction import Direction
from core.mis.service_client import Mis


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.mixins.RestListMixin,
             core.generic.views.ListView):
    template_name = 'core/directions/list.html'
    form_class = forms.DirectionSearch
    title = 'Направления'
    permission_required = 'core.view_direction'
    paginate_by = 50
    mis_request_path = Mis.DIRECTIONS_LIST_URL

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]


class Edit(PermissionRequiredMixin, core.generic.views.EditView):
    template_name = 'core/directions/edit.html'
    form_class = forms.DirectionEdit
    data_method = 'post'
    pk = 'pk'

    def get_success_url(self):
        return reverse_lazy('core:direction_list')

    def get_permission_required(self):
        perm = 'core.add_direction'
        if self.get_object():
            perm = 'core.change_direction'

        return [perm]

    def get_initial(self):
        initial = super().get_initial()
        obj = self.get_object()
        if obj:
            initial.update(dataclasses.asdict(obj))

        return initial

    def get_object(self):
        object_pk = self.kwargs.get(self.pk_url_kwarg)
        if object_pk:
            self.object = Direction.get(direction_id=object_pk)

        return self.object

    def form_valid(self, form):
        # todo: отправка запроса на сохранение в МИС
        return redirect(self.get_success_url())

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            ('Направления', reverse('core:direction_list')),
            (self.get_title(), ''),
        ]
