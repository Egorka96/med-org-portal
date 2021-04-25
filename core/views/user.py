from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage, send_mail
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin

import core.generic.mixins
import core.generic.views

from core import forms, filters
from project import settings

User = get_user_model()


class Search(PermissionRequiredMixin, core.generic.mixins.FormMixin, core.generic.views.ListView):
    template_name = 'core/user/list.html'
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
        return reverse_lazy('core:user')

    def get_permission_required(self):
        perm = 'auth.add_user'
        if self.get_object():
            perm = 'auth.change_user'

        return [perm]

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def form_valid(self, form):
        email_to = form.cleaned_data['email']
        password = form.cleaned_data['new_password']
        login = form.cleaned_data['username']

        KAK_TO_NAZVANIYE = f"""
        Вам была создана учетная запись в личном кабинете медцентра "<название медцентра>".
        Адрес личного кабинета - <url портала>.
        Логин -  { login }
        Пароль - { password }
        """

        send_mail('Регистрация успешно завершена', KAK_TO_NAZVANIYE, settings.EMAIL_HOST_USER, [email_to])

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['user'] = self.request.user
        return c

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
            (user, reverse('core:user_edit', kwargs={'pk': user.id})),
            (self.breadcrumb, ''),
        ]
