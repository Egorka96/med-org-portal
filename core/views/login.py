from django.conf import settings
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.template import Template, Context
from django.urls import reverse_lazy
from django.views.generic import TemplateView

import core.generic.mixins
from core import models, forms
from core.datatools.password import create_password


class Login(LoginView):
    template_name = 'core/login.html'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        c['can_send_email_user_credentials'] = getattr(settings, 'EMAIL_HOST_USER', None)
        return c


class PasswordChangeRequired(PasswordChangeView):
    form_class = SetPasswordForm
    template_name = 'core/password_change.html'
    success_url = reverse_lazy('core:index')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.user.core.need_change_password = False
        self.request.user.core.save()
        return response


class PasswordForgot(core.generic.mixins.FormMixin, TemplateView):
    template_name = 'core/forgot_password.html'
    form_class = forms.PasswordForgotForm
    success_url = reverse_lazy('login')
    data_method = 'post'

    def post(self, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        email_to = form.cleaned_data['email']
        user_email = models.User.objects.get(django_user__email=email_to)
        password_new = create_password()

        if user_email:
            user_email.need_change_password = True
            user_email.django_user.set_password(password_new)
            user_email.django_user.save()
            user_email.save()
            email_text = self._send_mail_login(form, password_new)
            send_mail(f'Временный пароль для доступа в личный кабинет медцентра {settings.MED_CENTER_NAME}',
                      email_text, settings.EMAIL_HOST_USER, [email_to])

            messages.success(self.request, 'Сообщение с паролем отправлено на почту.')

        return redirect(self.get_success_url())

    def _send_mail_login(self, form, password_new):
        email_template = Template(settings.EMAIL_FORGOT_USER_TEXT)
        email_context = {
            "password": password_new,
            "med_center_name": settings.MED_CENTER_NAME,
            "portal_url": settings.PORTAL_URL,
        }
        email_text = email_template.render(Context(email_context))

        return email_text