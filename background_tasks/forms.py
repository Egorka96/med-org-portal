from django import forms
import core.forms
import core.models
from background_tasks import consts


class TaskSearch(forms.Form):
    STATUS_CHOICES = [('', '')] + list(consts.STATUS_CHOICES)

    name = forms.CharField(label='Название', required=False)
    user = forms.ModelChoiceField(label='Пользователи', required=False,
                                  queryset=core.models.User.objects.filter(django_user__background_tasks__isnull=False).distinct(),
                                  widget=forms.Select(attrs={'class': 'need-select2'}))
    created_from = core.forms.RusDateField(label='Создана с', initial=None, required=False)
    created_to = core.forms.RusDateField(label='Создана по', initial=None, required=False)
    status = forms.ChoiceField(label='Статус', required=False, choices=STATUS_CHOICES)

    def clean_user(self):
        user = self.cleaned_data.get('user')
        if user:
            return user.django_user.id
