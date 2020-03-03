import json
from typing import List

from django.db import models
from django.contrib.auth.models import User as DjangoUser

from core.mis.org import Org


class User(models.Model):
    django_user = models.OneToOneField(DjangoUser, related_name='core', on_delete=models.CASCADE)
    org_ids = models.CharField('ID организаций', max_length=255, help_text='список id организаций из внешней системы')
    valuable_service_ids = models.CharField('ID значимых услуг', max_length=255, blank=True,
                                            help_text='список id услуг из внешней системы, которые имеют значения для '
                                                      'пользователя.')

    class Meta:
        permissions = (
            ('view_workers_done_report', 'Просмотр отчета по прошедшим'),
        )

    def __str__(self):
        return str(self.django_user)

    def get_orgs(self) -> List[Org]:
        if not self.org_ids:
            return []

        return [Org.get(org_id=org_id) for org_id in json.loads(self.org_ids)]

    def get_valuable_services(self):
        # todo
        return
