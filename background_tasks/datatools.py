from django.utils.timezone import now

from background_tasks import models
from background_tasks import consts


def process_task(task: models.Task) -> models.Task:
    try:
        models.Task.objects.filter(id=task.id).update(status=consts.STATUS_IN_PROCESS, start_dt=now())

        func = task.get_func()
        params = task.get_params()
        func(background_task=task, **params)

    except Exception as ex:
        description = str(ex)

        models.Task.objects.filter(id=task.id).update(status=consts.STATUS_FAIL)
        models.Log.objects.create(
            task=task,
            description=description,
            status=consts.STATUS_FAIL,
        )

    models.Task.objects.filter(id=task.id).update(finish_dt=now())
    task = models.Task.objects.get(id=task.id)
    return task


def cancel_task(task: models.Task):
    if models.Task.objects.get(id=task.id).start_dt:
        raise Exception('Задача "%s" уже была запущена и не может быть отменена')

    models.Task.objects.filter(id=task.id).update(
        status=consts.STATUS_CANCEL,
        start_dt=now(),
        finish_dt=now(),
    )


def restart_task(task: models.Task):
    import background_tasks.tasks
    if models.Task.objects.get(id=task.id).in_progress():
        raise Exception('Задача "%s" уже была выполняется и не может быть перезапущена сейчас')

    models.Task.objects.filter(id=task.id).update(
        status=consts.STATUS_PENDING,
        percent=0,
        start_dt=None,
        finish_dt=None,
        result_attachment=None,
    )

    background_tasks.tasks.start_task.delay(task.id)
