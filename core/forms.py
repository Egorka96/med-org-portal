import datetime
import json

from django import forms
from django.contrib.auth import get_user_model

from core import models
from core.mis.org import Org
from core.mis.service_client import Mis

User = get_user_model()


class RusDateField(forms.DateField):
    def __init__(self, input_format='%d.%m.%Y', *args, **kwargs):
        kwargs['input_formats'] = [input_format]
        if 'initial' not in kwargs:
            kwargs['initial'] = lambda: datetime.date.today().strftime('%d.%m.%Y')
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.TextInput(attrs={'class': 'date'})
        super().__init__(*args, **kwargs)
        self.input_format = input_format

    def to_python(self, value):
        if value:
            # если уже дата вернем как есть
            if isinstance(value, datetime.datetime):
                return value.date()
            if isinstance(value, datetime.date):
                return value
            try:
                return datetime.datetime.strptime(value, self.input_format).date()
            except ValueError:
                raise forms.ValidationError(self.error_messages['invalid'])
        else:
            return None

    def validate(self, value):
        super(RusDateField, self).validate(value)
        if not value:
            return

        if value.year < 1900:
            raise forms.ValidationError(u'Год должен быть больше 1900')

        if isinstance(value, datetime.date):
            return

        try:
            return datetime.datetime.strptime(value, self.input_format).date()
        except ValueError:
            raise forms.ValidationError(u'Используйте формат ДД.ММ.ГГГГ')

    def prepare_value(self, value):
        if isinstance(value, datetime.date):
            return value.strftime(self.input_format)
        return value


class ListField(forms.MultipleChoiceField):
    @staticmethod
    def valid_value(*args, **kwargs) -> bool:
        return True


class OrgsMixin(forms.Form):
    orgs = ListField(label='Организации', choices=[], required=False)

    class Media:
        js = ['core/js/orgs.js']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = []

        values = self.data.getlist('orgs') if hasattr(self.data, 'getlist') else self.initial.get('orgs', [])
        if values:
            for value in values:
                org = Org.get(org_id=value)
                choices.append((org.id, org.name))

        self.fields['orgs'].widget.choices = choices


class DateFromTo(forms.Form):
    date_from = RusDateField(label='С', required=False, initial=None)
    date_to = RusDateField(label='По', required=False, initial=None)


class ExamTypeMixin(forms.Form):
    EXAM_TYPE_CHOICES = (
        ('', '---------'),
        ('Предварительный', 'Предварительный'),
        ('Периодический', 'Периодический'),
        ('Внеочередной', 'Внеочередной'),
    )
    exam_type = forms.ChoiceField(label='Вид осмотра', required=False, choices=EXAM_TYPE_CHOICES)


class PlaceMixin(forms.Form):
    PLACE_CHOICES = (
        ('', '---------'),
        ('Медцентр', 'Медцентр'),
        ('Выезд', 'Выезд'),
    )
    place = forms.ChoiceField(label='Место', help_text='место проведения осмотра', choices=PLACE_CHOICES,
                              required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not Mis().is_out_used():
            self.fields['place'].widget = forms.HiddenInput()


class UserSearch(forms.Form):
    username = forms.CharField(label='Логин', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    is_active = forms.NullBooleanField(label='Активен', required=False, initial=True)


class UserEdit(OrgsMixin, forms.ModelForm):
    new_password = forms.CharField(label='Новый пароль', required=False)

    class Meta:
        model = User
        exclude = ['password', 'date_joined', 'last_login', 'is_staff']
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

        if perm_groups := self.cleaned_data.get('groups'):
            user.groups.set(perm_groups)

        if not hasattr(user, 'core'):
            user.mis = models.User.objects.create(django_user=user)

        user.core.org_ids = json.dumps(self.cleaned_data.get('orgs', []))
        user.core.save()


class WorkersPastReport(DateFromTo, OrgsMixin, ExamTypeMixin, PlaceMixin, forms.Form):
    last_name = forms.CharField(label='Фамилия', required=False)
    first_name = forms.CharField(label='Имя', required=False)
    middle_name = forms.CharField(label='Отчество', required=False)

    shop = forms.CharField(label='Подразделение', required=False)
    post = forms.CharField(label='Должность', required=False)


class DirectionSearch(DateFromTo, OrgsMixin, forms.Form):
    last_name = forms.CharField(label='Фамилия', required=False)
    first_name = forms.CharField(label='Имя', required=False)
    middle_name = forms.CharField(label='Отчество', required=False)

    shop = forms.CharField(label='Подразделение', required=False)
    post = forms.CharField(label='Должность', required=False)

    confirmed = forms.NullBooleanField(label='Подтвержден', required=False)
