import os
import pickle
import tempfile
from typing import Callable, Dict
import importlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.validators import MaxValueValidator
from django.db import models
import core.models
from background_tasks import consts

User = get_user_model()


class Task(models.Model):
    name = models.CharField('Название задачи', max_length=255)
    description = models.TextField('Описание задачи', blank=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', null=True, blank=True,
                             related_name='background_tasks', help_text='Пользователь, создавший задачу',
                             on_delete=models.PROTECT)

    func_path = models.CharField('Функция для вызова', max_length=255)
    params = models.FileField('Параметры', null=True, blank=True,
                              upload_to=lambda t, f_name: 'background_tasks/params_pickle/%s/%s' % (t.id, f_name),
                              help_text='Параметры, сериализованные в формате pickle')

    status = models.CharField('Статус выполнения задачи', choices=consts.STATUS_CHOICES,
                              default=consts.STATUS_PENDING, max_length=255, db_index=True)
    percent = models.PositiveSmallIntegerField('Процент выполнения', default=0, validators=[MaxValueValidator(100)])

    created_dt = models.DateTimeField('Создана', auto_now_add=True)
    start_dt = models.DateTimeField('Время начала выполнения задачи', null=True, blank=True)
    finish_dt = models.DateTimeField('Время окончания выполнения задачи', null=True, blank=True)

    result_attachment = models.FileField('Результат', null=True, blank=True,
                                         upload_to=lambda t, f_name: 'background_tasks/results/%s/%s' % (t.id, f_name))

    class Meta:
        verbose_name = 'Фоновая задача'
        verbose_name_plural = 'Фоновые задачи'
        ordering = ('-created_dt', )

    @classmethod
    def create_task(cls, method: Callable, name: str, user: 'core.models.DjangoUser', params: Dict,
                    description: str = '', create_notification: bool = False) -> 'Task':
        from background_tasks.tasks import start_task

        func_path = f"{method.__self__.__module__}.{method.__self__.__qualname__}.{method.__name__}"
        task = cls.objects.create(
            name=name,
            description=description,
            user=user,
            func_path=func_path
        )

        task.save_params(params)
        start_task.delay(task.id, create_notification=create_notification)

        return task

    @staticmethod
    def pickle_params(params: dict) -> str:
        """Сериализует параметры и возвращает путь к файлу с сериализованными данными"""
        if not os.path.exists(settings.DIR_FOR_TMP_FILES):
            os.makedirs(settings.DIR_FOR_TMP_FILES)

        pickled_path = tempfile.mkdtemp(dir=settings.DIR_FOR_TMP_FILES) + '/data.pickle'

        with open(pickled_path, 'wb') as f:
            pickle.dump(params, f)

        return pickled_path

    def save_params(self, params: dict):
        pickled_params_path = self.pickle_params(params)
        with open(pickled_params_path, 'rb') as f:
            self.params.save(name='params.pickle', content=File(f))
        os.unlink(pickled_params_path)

    def __str__(self):
        return self.name

    def get_func(self) -> Callable:
        try:
            # функция в пакете
            module_path = '.'.join(i for i in self.func_path.split('.')[:-1])
            func_name = self.func_path.split('.')[-1]
            module = importlib.import_module(module_path)
            return getattr(module, func_name)
        except ImportError:
            # метод класса
            module_path = '.'.join(i for i in self.func_path.split('.')[:-2])
            class_name = self.func_path.split('.')[-2]
            func_name = self.func_path.split('.')[-1]
            module = importlib.import_module(module_path)
            class_obj = getattr(module, class_name)
            return getattr(class_obj, func_name)

    def get_params(self) -> dict:
        if self.params:
            with open(self.params.path, 'rb') as f:
                return pickle.load(self.params)
        else:
            return {}

    def is_success(self) -> bool:
        return self.finish_dt and self.status == consts.STATUS_COMPLETE

    def is_fail(self) -> bool:
        return self.status == consts.STATUS_FAIL

    def in_progress(self) -> bool:
        return self.status == consts.STATUS_IN_PROCESS


class Log(models.Model):
    task = models.ForeignKey(Task, related_name='logs', on_delete=models.CASCADE)
    description = models.TextField('Описание')
    status = models.CharField('Статус выполнения задачи', choices=consts.STATUS_CHOICES,
                              default=consts.STATUS_IN_PROCESS, max_length=255, db_index=True)
    dc = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Запись журнала выполнения задачи'
        verbose_name_plural = 'Журнал выполнения задачи'
        ordering = ('-dc', )

    def is_success(self) -> bool:
        return self.status == consts.STATUS_COMPLETE

    def is_fail(self) -> bool:
        return self.status == consts.STATUS_FAIL
