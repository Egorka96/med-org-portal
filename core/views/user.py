from django.contrib.auth import get_user_model
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin

import core.generic.mixins
import core.generic.views

from core import forms, filters

User = get_user_model()


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.views.ListView):
    template_name = 'core/user/search.html'
    model = User
    form_class = forms.UserSearch
    filter_class = filters.User
    title = 'Пользователи'
    permission_required = 'auth.view_user'

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            (self.title, ''),
        ]

    def get_queryset(self):
        return super().get_queryset().distinct().order_by('username')


class Edit(PermissionRequiredMixin, core.generic.views.EditView):
    template_name = 'core/user/edit.html'
    model = User
    data_method = 'post'
    form_class = forms.UserEdit
    pk = 'pk'

    def get_success_url(self):
        return reverse_lazy('conf:core_user')

    def get_permission_required(self):
        perm = 'auth.add_user'
        if self.get_object():
            perm = 'auth.change_user'

        return [perm]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def get_breadcrumbs(self):
        return [
            ('Главная', reverse('core:index')),
            ('Пользователи', reverse('core:user')),
            (self.get_title(), ''),
        ]


class Delete(PermissionRequiredMixin, core.generic.views.DeleteView):
    success_url = reverse_lazy('core:user')
    breadcrumb = 'Удалить'
    model = User
    permission_required = 'auth.delete_user'

    def get_breadcrumbs(self):
        user = self.get_object()
        return [
            ('Главная', reverse('core:index')),
            ('Пользователи', reverse('core:user')),
            (user, reverse('conf:core_user_edit', kwargs={'pk': user.id})),
            (self.breadcrumb, ''),
        ]
