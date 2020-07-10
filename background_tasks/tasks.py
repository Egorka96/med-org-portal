from project import celery_app
from background_tasks import models
from background_tasks import datatools


@celery_app.task()
def start_task(task_id):
    task = models.Task.objects.get(id=task_id)
    if task.start_dt:
        return

    datatools.process_task(task)
