import json
from typing import List

from django.db import models
from django.contrib.auth.models import User as DjangoUser

from mis.org import Org


class User(models.Model):
    django_user = models.OneToOneField(DjangoUser, related_name='core', on_delete=models.CASCADE)
    org_ids = models.CharField('ID организаций', max_length=255, help_text='список id организаций из внешней системы')

    class Meta:
        permissions = (
            ('view_workers_done_report', 'Просмотр отчета по прошедшим'),

            ('view_direction', 'Просмотр направлений на осмотр'),
            ('add_direction', 'Создание направлений на осмотр'),
            ('change_direction', 'Редактирование направлений на осмотр'),
            ('delete_direction', 'Удаление направлений на осмотр'),
        )

    def __str__(self):
        return str(self.django_user)

    def get_orgs(self) -> List[Org]:
        if not self.org_ids:
            return []

        return [Org.get(org_id=org_id) for org_id in json.loads(self.org_ids)]
