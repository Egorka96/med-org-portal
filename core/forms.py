import json

from django import forms
from django.contrib.auth import get_user_model

from core import models

User = get_user_model()


class ListField(forms.MultipleChoiceField):
    @staticmethod
    def valid_value(*args, **kwargs) -> bool:
        return True


class OrgsMixin(forms.Form):
    orgs = ListField(label='Организации', choices=[], required=False)

    class Media:
        js = ['core/js/orgs.js']


class UserSearch(forms.Form):
    username = forms.CharField(label='Логин', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    is_active = forms.NullBooleanField(label='Активен', required=False, initial=True)


class UserEdit(OrgsMixin, forms.ModelForm):
    new_password = forms.CharField(label='Новый пароль', required=False)

    class Meta:
        model = User
        exclude = ['password', 'date_joined', 'last_login']
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'need-select2'}),
            'user_permissions': forms.SelectMultiple(attrs={'class': 'need-select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'

        if getattr(self.instance, 'core', None):
            orgs = self.instance.core.get_orgs()
            self.initial['orgs'] = [str(org.id) for org in orgs]
            self.fields['orgs'].widget.choices = [(str(org.id), org.name) for org in orgs]

    def save(self, *args, **kwargs):
        new_password = self.cleaned_data.get('new_password')

        user = super().save(commit=False)

        if user.pk:
            user.password = User.objects.get(pk=user.pk).password

        if new_password:
            user.set_password(new_password)

        user.save()

        if not hasattr(user, 'core'):
            user.mis = models.User.objects.create(django_user=user)

        if orgs := self.cleaned_data.get('orgs'):
            user.core.org_ids = json.dumps(orgs)

        user.core.save()

        if self.fields.get('user_permissions'):
            user_permissions = self.cleaned_data.get('user_permissions', [])
            user.user_permissions.clear()
            user.user_permissions.add(*user_permissions)

        return user
