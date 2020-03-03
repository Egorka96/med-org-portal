import django_filters
from django.contrib.auth import get_user_model

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
