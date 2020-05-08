from django.urls import path
from rest_framework import routers

import background_tasks.views.task
import background_tasks.views.rest

app_name = 'background_task'

urlpatterns = [
    path('', background_tasks.views.task.Search.as_view(), name='task_search'),
    path('<int:pk>/', background_tasks.views.task.Detail.as_view(), name='task_info'),
    path('<int:pk>/cancel/', background_tasks.views.task.Cancel.as_view(), name='task_cancel'),
    path('<int:pk>/restart/', background_tasks.views.task.Restart.as_view(), name='task_restart'),
]


router = routers.DefaultRouter()
router.register('rest/task', background_tasks.views.rest.TaskViewSet)
urlpatterns += router.urls
