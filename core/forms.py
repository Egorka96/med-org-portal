import datetime
import json

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from core import models
from mis.law_item import LawItem
from mis.org import Org
from mis.service_client import Mis
from mis.pay_method import PayMethod as MisPayMethod
from mis.document import DocumentType as MisDocumentType

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
                values = self.initial.get(field, [])

            if not isinstance(values, list):
                values = [values]

            if values:
                for value in values:
                    if not value:
                        continue

                    org = Org.get(org_id=value)
                    choices.append((org.id, str(org)))

            self.fields[field].widget.choices = choices


class LawItems(forms.Form):
    law_items_302_section_1 = ListField(label='Пункты приказа 302н прил.1', required=False, choices=[])
    law_items_302_section_2 = ListField(label='Пункты приказа 302н прил.2', required=False, choices=[])
    law_items_29 = ListField(label='Пункты приказа 29н', required=False, choices=[])

    class Media:
        js = ['core/js/law_items.js']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in ('law_items_302_section_1', 'law_items_302_section_2', 'law_items_29'):
            choices = []
            values = self.data.getlist(field) if hasattr(self.data, 'getlist') else None
            if not values:
                values = self.initial.get(field, [])

            if values and not isinstance(values, list):
                values = [values]

            if values:
                for value in values:
                    law_item = LawItem.get(law_item_id=value)
                    choices.append((law_item.id, law_item.name))

            self.fields[field].widget.choices = choices

    def clean(self):
        law_items_302n = [*self.cleaned_data.get('law_items_302_section_1', []),
                          *self.cleaned_data.get('law_items_302_section_2', [])]
        law_items_29n = self.cleaned_data.get('law_items_29', [])

        if law_items_302n and law_items_29n:
            raise forms.ValidationError('Необходимо указать пункты приказа 302н ИЛИ 29н.')

        return self.cleaned_data


class DocumentTypeMixin(forms.Form):
    document_types = ListField(label='Виды документов', help_text='для печати из МИС', required=False, choices=[],
                               widget=forms.SelectMultiple(attrs={'class': 'need-select2'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document_types'].widget.choices = [(d_t.id, d_t.name) for d_t in MisDocumentType.filter()]


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


class UserEdit(OrgsMixin, DocumentTypeMixin, forms.ModelForm):
    new_password = forms.CharField(label='Новый пароль', required=False, validators=[validate_password],
                                   help_text='<div>Пароль не должен совпадать с именем или другой персональной '
                                             'информацией пользователя или быть слишком похожим на неё. </div>'
                                             '<div>Пароль должен содержать как минимум 8 символов. </div>'
                                             '<div>Пароль не может быть одним из широко распространённых паролей. </div>'
                                             '<div>Пароль не может состоять только из цифр. </div>')
    post = forms.CharField(label='Должность', required=False)

    class Meta:
        model = User
        exclude = ['password', 'date_joined', 'last_login', 'is_staff', ]
        widgets = {
            'groups': forms.SelectMultiple(attrs={'class': 'need-select2'}),
            'user_permissions': forms.SelectMultiple(attrs={'class': 'need-select2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['email'].label = 'Email'
        self.fields['email'].help_text = 'адрес электронной почты'

        if getattr(self.instance, 'core', None):
            orgs = self.instance.core.get_orgs()
            self.initial['orgs'] = [str(org.id) for org in orgs]
            self.fields['orgs'].widget.choices = [(str(org.id), org.name) for org in orgs]

            self.initial['document_types'] = [str(d_t.id) for d_t in self.instance.core.get_available_document_types()]
            self.initial['post'] = self.instance.core.post

        self.fields['orgs'].help_text = 'к каким организациям пользователь должен иметь доступ. ' \
                                        'Оставьте поле пустым, если пользователь должен иметь доступ ко всем ' \
                                        'доступным организациям'
        self.fields['document_types'].help_text = 'какие виды документов доступны пользователю для печати'

    def clean_email(self):
        value = self.cleaned_data.get('email')
        if not value:
            return

        # будем требовать, чтобы email пользователей был уникален
        email_users = User.objects.filter(email=value)
        if self.instance:
            email_users = email_users.exclude(id=self.instance.id)

        if email_users:
            raise forms.ValidationError(f'Указанный email уже связан с пользователем "{email_users.first()}"')

        return value

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
        user.core.post = self.cleaned_data.get('post')
        user.core.save()

        if document_type_ids := self.cleaned_data.get('document_types', []):
            for d_t_id in document_type_ids:
                user.core.available_document_type_ids.get_or_create(document_type_id=d_t_id)

            user.core.available_document_type_ids.exclude(document_type_id__in=document_type_ids).delete()

        return user


class WorkerSearch(FIO, OrgsMixin, forms.Form):
    ACTIVE_CHOICES = (
        ('', '---------'),
        ('1', 'Работает'),
        ('0', 'Уволен'),
    )

    shop = forms.CharField(label='Подразделение', required=False)
    post = forms.CharField(label='Должность', required=False)
    is_active = forms.ChoiceField(label='Работает', choices=ACTIVE_CHOICES, required=False, initial='1')


class WorkersPastReport(FIO, DateFromTo, OrgsMixin, ExamTypeMixin, PlaceMixin, forms.Form):
    shop = forms.CharField(label='Подразделение', required=False)
    post = forms.CharField(label='Должность', required=False)

    def clean(self):
        cleaned_data = super().clean()
        workers = [v for v in cleaned_data.values() if v]
        if not workers:
            raise forms.ValidationError(
                    "Введите параметры фильтрации."
                )


class DirectionSearch(FIO, DateFromTo, OrgsMixin, forms.Form):
    shop = forms.CharField(label='Подразделение', required=False)
    post = forms.CharField(label='Должность', required=False)
    confirmed = forms.NullBooleanField(label='Подтвержден', required=False)

    def clean_confirmed(self):
        value = self.cleaned_data.get('confirmed')
        if value is None:
            return

        # возвращаем в формате, ожидаемому МИС
        return int(value)


class DirectionEdit(FIO, OrgsMixin, ExamTypeMixin, LawItems, PayMethod, forms.Form):
    GENDER_CHOICE = (
        ('Мужской', 'Мужской'),
        ('Женский', 'Женский'),
    )

    gender = forms.ChoiceField(label='Пол', choices=GENDER_CHOICE, required=False)
    birth = RusDateField(label='Дата рождения', initial=None)
    post = forms.CharField(label='Должность', required=False)
    shop = forms.CharField(label='Подразделение', required=False)
    insurance_number = forms.CharField(label='Страховой полис',help_text="Полис ОМС или ДМС", required=False)

    def __init__(self, *args, current_user, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['last_name'].required = True
        self.fields['first_name'].required = True
        self.fields['exam_type'].required = True
        self.fields['exam_type'].initial = 'Периодический'

        user_orgs = current_user.core.get_orgs()
        if user_orgs and len(user_orgs) < 2:
            org = user_orgs[0]
            self.fields['org'].initial = org.id
            self.fields['org'].choices = [(org.id, str(org))]
            self.fields['org'].widget = forms.HiddenInput()


class PasswordForgotForm(forms.Form):
    email = forms.EmailField(required=False)

    def clean_email(self):
        value = self.cleaned_data.get('email')

        user_qs = models.User.objects.filter(django_user__email=value)
        err_msg = ''

        if user_qs:
            if user_qs.count() > 1:
                err_msg = "У этой почты множество аккаунтов."
        else:
            err_msg = "Этого пользователя не существует."

        if err_msg:
            raise forms.ValidationError(err_msg)

        return value
