import django_filters
from django.contrib.auth import get_user_model

from core import models

DjangoUser = get_user_model()


class User(django_filters.FilterSet):
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains')
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter(method='filter_is_active')

    class Meta:
        model = DjangoUser
        fields = ['username', 'last_name', 'is_active']

    def filter_is_active(self, qs, name, value):
        return qs.filter(is_active=value)


class Worker(django_filters.FilterSet):
    last_name = django_filters.CharFilter(field_name='last_name', lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name='first_name', lookup_expr='icontains')
    middle_name = django_filters.CharFilter(field_name='middle_name', lookup_expr='icontains')
    post = django_filters.CharFilter(field_name='worker_orgs__post', lookup_expr='icontains')
    shop = django_filters.CharFilter(field_name='worker_orgs__shop', lookup_expr='icontains')
    orgs = django_filters.CharFilter(method='filter_orgs')
    is_active = django_filters.CharFilter(method='filter_is_active')

    class Meta:
        model = models.Worker
        fields = '__all__'

    def filter_orgs(self, qs, name, value):
        return qs.filter(worker_orgs__org_id__in=value)

    def filter_is_active(self, qs, name, value):
        if value:
            qs = qs.filter(worker_orgs__end_work_date__isnull=int(value))
        return qs
