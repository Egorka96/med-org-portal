import json
from typing import List

import djutils.models
import sw_logger.models
from django.db import models
from django.contrib.auth.models import User as DjangoUser
from sw_logger.tools import get_model_by_log_name
from core import consts

from mis.document import DocumentType
from mis.org import Org


def docx_file_extension(value):
    """Валидация раширения файла для FileField(validators=[docx_file_extension])"""
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.docx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Поддерживается только формат файла docx.')


class Status(djutils.models.OneValueModel):
    WORKER_LOAD_TIME = 'worker_load_time'

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def __str__(self):
        return self.name


class User(models.Model):
    django_user = models.OneToOneField(DjangoUser, related_name='core', on_delete=models.CASCADE)
    org_ids = models.CharField('ID организаций', max_length=255, help_text='список id организаций из внешней системы')
    post = models.CharField('Должность', max_length=255, blank=True)
    need_change_password = models.BooleanField('Нужно сменить пароль', default=True)

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

    def get_org_ids(self):
        if not self.org_ids:
            return []
        return json.loads(self.org_ids)

    def get_orgs(self) -> List[Org]:
        if not self.org_ids:
            return []

        return [Org.get(org_id=org_id) for org_id in self.get_org_ids()]

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
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    middle_name = models.CharField(max_length=255, verbose_name='Отчество', blank=True)
    gender = models.CharField(max_length=7, verbose_name='Пол', choices=consts.GENDER_CHOICE)
    birth = models.DateField(verbose_name='Дата рождение')
    note = models.TextField(blank=True, verbose_name='Примечание')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['last_name', 'first_name', 'middle_name']
        permissions = (
            ('view_workers_document', 'Просмотр документов сотрудника'),
        )

    def __str__(self):
        return ' '.join(filter(bool, [self.last_name, self.first_name, self.middle_name]))

    def get_posts(self):
        return ', '.join(set(self.worker_orgs.exclude(post="").values_list('post', flat=True)))

    def get_shops(self):
        return ', '.join(set(self.worker_orgs.exclude(shop="").values_list('shop', flat=True)))


class WorkerOrganization(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, verbose_name='Сотрудник', related_name='worker_orgs')
    mis_id = models.IntegerField(verbose_name='МИС id')
    org_id = models.IntegerField(verbose_name='Организация id')
    post = models.CharField(max_length=512, verbose_name='Должность')
    shop = models.CharField(max_length=512, verbose_name='Подразделение', blank=True)
    start_work_date = models.DateField(null=True, blank=True, verbose_name='Дата приема')
    end_work_date = models.DateField(null=True, blank=True, verbose_name='Дата уволения')

    class Meta:
        verbose_name = 'Сотрудник организации'
        verbose_name_plural = 'Сотрудники организации'


class Direction(models.Model):
    EXAM_TYPE_CHOICE = [
        ('Предварительный', 'Предварительный'),
        ('Периодический', 'Периодический'),
        ('Внеочередной', 'Внеочередной')
    ]

    worker = models.ForeignKey(Worker, on_delete=models.PROTECT, verbose_name='Сотрудник', related_name='worker_directions')
    mis_id = models.IntegerField(verbose_name='МИС id', unique=True, null=True)
    insurance_policy = models.CharField(verbose_name='Cтраховой полис', max_length=255, blank=True)
    org_id = models.IntegerField(verbose_name='Организация id', null=True, blank=True)
    post = models.CharField(verbose_name='Должность', blank=True, max_length=255,)
    shop = models.CharField(verbose_name='Подразделение', blank=True, max_length=255,)
    exam_type = models.CharField(verbose_name='Вид осмотра', choices=EXAM_TYPE_CHOICE, max_length=255)
    pay_method = models.CharField(verbose_name='Cпособ оплаты', max_length=255,)

    class Meta:
        verbose_name = 'Направление'
        verbose_name_plural = 'Направление'

    def __str__(self):
        return f'Направление №{self.mis_id}'


class DirectionLawItem(models.Model):
    direction = models.ForeignKey(Direction, on_delete=models.PROTECT, verbose_name='Направление',)
    law_item_mis_id = models.CharField(verbose_name='Пункты приказа', max_length=255,)

    class Meta:
        verbose_name = 'Пункты приказа'
        verbose_name_plural = 'Пункты приказа'

    def __str__(self):
        return f'Пункт приказа {self.direction}'


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


class Log(sw_logger.models.Log):

    class Meta:
        ordering = ('id',)
        verbose_name = 'Запись в журнале'
        verbose_name_plural = 'Журнал'

    def get_model_object(self, include_deleted=True):
        model = get_model_by_log_name(self.object_name)
        manager = 'standard_objects' if hasattr(model, 'standard_objects') and include_deleted else 'objects'
        return getattr(model, manager).filter(id=self.object_id).first()
