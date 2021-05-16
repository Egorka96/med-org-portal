from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordChangeView
from django.core.mail import EmailMessage, send_mail
from django.shortcuts import redirect
from django.template import Template, Context
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin

import core.generic.mixins
import core.generic.views

from core import forms, filters

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
        instance = form.save()
        if self.request.POST.get('send_email_user_credentials'):
            self._send_user_credentials(form, instance)

        return redirect(self.get_success_url())

    def _send_user_credentials(self, form, user):
        email_template = Template(settings.EMAIL_USER_CREDENTIALS_TEXT)
        email_context = {
            "login": form.cleaned_data['username'],
            "password": form.cleaned_data['new_password'],
            "med_center_name": settings.MED_CENTER_NAME,
            "portal_url": settings.PORTAL_URL,
        }
        send_mail(
            f'Регистрация пользователя в личном кабинете медцентра "{settings.MED_CENTER_NAME}"',
            email_template.render(Context(email_context)),
            settings.EMAIL_HOST_USER,
            [form.cleaned_data['email']]
        )

        user.core.need_change_password = True
        user.core.save()

        messages.success(self.request, f'Учетные данные пользователя отправлены на почту {form.cleaned_data["email"]}')

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


class PasswordChangeRequired(PasswordChangeView):
    form_class = SetPasswordForm
    template_name = 'core/required_password_change.html'
    success_url = reverse_lazy('core:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.core.need_change_password = False
        self.request.user.core.save()
        return response
