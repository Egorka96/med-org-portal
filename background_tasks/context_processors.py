from background_tasks import models


def user_background_tasks(request):
    if request.user.is_anonymous:
        return {}
    else:
        return {
            'user_background_tasks': models.Task.objects.filter(user=request.user),
            'user_background_active_tasks': models.Task.objects.filter(user=request.user, finish_dt__isnull=True),
        }

