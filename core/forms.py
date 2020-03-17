import datetime
import json

from django import forms
from django.contrib.auth import get_user_model

from core import models
from core.mis.law_item import LawItem
from core.mis.org import Org
from core.mis.service_client import Mis
from core.mis.pay_method import PayMethod as MisPayMethod

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


class ExtraChoiceField(forms.ChoiceField):
    @staticmethod
    def valid_value(*args, **kwargs) -> bool:
        return True


class ListField(forms.MultipleChoiceField):
    @staticmethod
    def valid_value(*args, **kwargs) -> bool:
        return True


class FIO(forms.Form):
    last_name = forms.CharField(label='Фамилия', required=False)
    first_name = forms.CharField(label='Имя', required=False)
    middle_name = forms.CharField(label='Отчество', required=False)


class PayMethod(forms.Form):
    pay_method = ExtraChoiceField(label='Способ оплаты', choices=[], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pay_method'].widget.choices = [('', '----------')] + \
                                                   [(p_m.id, p_m.name) for p_m in MisPayMethod.filter()]


class OrgsMixin(forms.Form):
    org = ExtraChoiceField(label='Организация', choices=[], required=False)
    orgs = ListField(label='Организации', choices=[], required=False)

    class Media:
        js = ['core/js/orgs.js']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in ('org', 'orgs'):
            choices = []
            values = self.data.getlist(field) if hasattr(self.data, 'getlist') else None
            if not values:
                values =  self.initial.get(field, [])

            if not isinstance(values, list):
                values = [values]

            if values:
                for value in values:
                    org = Org.get(org_id=value)
                    choices.append((org.id, org.name))

            self.fields[field].widget.choices = choices


class LawItems(forms.Form):
    law_items_section_1 = ListField(label='Пункты приказа прил.1', required=False, choices=[])
    law_items_section_2 = ListField(label='Пункты приказа прил.2', required=False, choices=[])

    class Media:
        js = ['core/js/law_items.js']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in ('law_items_section_1', 'law_items_section_2'):
            choices = []
            values = self.data.getlist(field) if hasattr(self.data, 'getlist') else None
            if not values:
                values =  self.initial.get(field, [])

            if values and not isinstance(values, list):
                values = [values]

            if values:
                for value in values:
                    law_item = LawItem.get(law_item_id=value)
                    choices.append((law_item.id, law_item.name))

            self.fields[field].widget.choices = choices


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


class WorkersPastReport(FIO, DateFromTo, OrgsMixin, ExamTypeMixin, PlaceMixin, forms.Form):
    shop = forms.CharField(label='Подразделение', required=False)
    post = forms.CharField(label='Должность', required=False)


class DirectionSearch(FIO, DateFromTo, OrgsMixin, forms.Form):
    shop = forms.CharField(label='Подразделение', required=False)
    post = forms.CharField(label='Должность', required=False)
    confirmed = forms.NullBooleanField(label='Подтвержден', required=False)


class DirectionEdit(FIO, OrgsMixin, ExamTypeMixin, LawItems, PayMethod, forms.Form):
    GENDER_CHOICE = (
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
    )

    gender = forms.ChoiceField(label='Пол', choices=GENDER_CHOICE, required=False)
    birth = RusDateField(label='Дата рождения', initial=None)
    post = forms.CharField(label='Должность', required=False)
    shop = forms.CharField(label='Подразделение', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['last_name'].required = True
        self.fields['first_name'].required = True
        self.fields['exam_type'].required = True
        self.fields['exam_type'].initial = 'Периодический'
