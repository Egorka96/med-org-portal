import django_filters
from django.contrib.auth import get_user_model

from background_tasks import models


User = get_user_model()


class Task(django_filters.FilterSet):
    id = django_filters.Filter(method='filter_id')
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    created_from = django_filters.DateFilter(field_name='created_dt__date', lookup_expr='gte')
    created_to = django_filters.DateFilter(field_name='created_dt__date', lookup_expr='lte')

    class Meta:
        model = models.Task
        fields = ('status', 'func_path')

    def filter_id(self, qs, _, value):
        ids = self.request.GET.getlist('id')
        if ids:
            qs = qs.filter(id__in=ids)
        return qs
