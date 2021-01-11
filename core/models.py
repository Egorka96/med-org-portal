import json
from typing import List

from django.db import models
from django.contrib.auth.models import User as DjangoUser

from mis.document_type import DocumentType
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
    post = models.CharField('Должность', max_length=255, blank=True)

    class Meta:
        permissions = (
            ('view_workers_done_report', 'Просмотр отчета по прошедшим'),
            ('view_money', 'Просмотр денежной информации'),

            ('view_direction', 'Просмотр направлений на осмотр'),
            ('add_direction', 'Создание направлений на осмотр'),
            ('change_direction', 'Редактирование направлений на осмотр'),
            ('delete_direction', 'Удаление направлений на осмотр'),
        )

    def __str__(self):
        return str(self.django_user)

    def get_fio(self):
        return ' '.join(filter(bool, [self.django_user.last_name, self.django_user.first_name]))

    def get_short_fio(self):
        if self.django_user.first_name.strip():
            return f'{self.django_user.last_name} {self.get_initials()}'
        else:
            return self.get_fio()

    def get_initials(self):
        if not self.django_user.first_name.strip():
            return ''

        parts = self.django_user.first_name.split(' ')
        if not parts:
            return ''

        initials = '%s.' % parts[0][0]
        if len(parts) > 1:
            initials += '%s.' % parts[1][0]
        return initials

    def get_orgs(self) -> List[Org]:
        if not self.org_ids:
            return []

        return [Org.get(org_id=org_id) for org_id in json.loads(self.org_ids)]

    def get_available_document_types(self) -> List[DocumentType]:
        user_doc_type_ids = self.available_document_type_ids.values_list('document_type_id', flat=True)
        return [DocumentType.get(document_type_id=d_t_id) for d_t_id in user_doc_type_ids]


class UserAvailableDocumentType(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE,
                             related_name='available_document_type_ids')
    document_type_id = models.IntegerField('ID вида документа в МИС')

    class Meta:
        verbose_name = 'Доступный вид документа для пользователя'
        verbose_name_plural = 'Доступные виды документов для пользователей'
        unique_together = ('user', 'document_type_id')


class Worker(models.Model):

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


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
