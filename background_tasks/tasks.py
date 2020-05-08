from django.urls import reverse

from project import celery_app
from background_tasks import models
from background_tasks import datatools
import core.models


@celery_app.task()
def start_task(task_id, create_notification=False):
    task = models.Task.objects.get(id=task_id)
    if task.start_dt:
        return

    datatools.process_task(task)

    if task.user and create_notification:
        core.models.Notification.objects.create(
            target_user=task.user,
            message='Выполнена фоновая задача "%s"' % task,
            url=reverse('background_tasks:task_info', kwargs={'pk': task.id}),
            url_label='Фоновые задачи',
        )
