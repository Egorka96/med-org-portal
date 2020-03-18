import json
from typing import List

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.contrib.auth.models import User as DjangoUser

from mis.org import Org


def docx_file_extension(value):
    """Валидация раширения файла для FileField(validators=[docx_file_extension])"""
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Поддерживается только формат файла docx.')


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


class DirectionDocxTemplate(models.Model):
    name = models.CharField('Название', max_length=255, unique=True)
    description = models.TextField('Описание', blank=True)
    org_ids = models.CharField('Список ID организаций', max_length=255,
                               help_text='список id организаций из внешней системы', blank=True)
    file = models.FileField('Файл шаблона', upload_to='core/direction_docx_templates/',
                            validators=[docx_file_extension])

    class Meta:
        verbose_name = 'Шаблон направления на осмотр'
        verbose_name_plural = 'Шаблоны направлений на осмотр'
        ordering = ('name', )

    def __str__(self):
        return self.name

    def get_orgs(self) -> List[Org]:
        if not self.org_ids:
            return []

        return [Org.get(org_id=org_id) for org_id in json.loads(self.org_ids)]
