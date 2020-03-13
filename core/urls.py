from django.urls import path

from core.views import index
from core.views import user
from core.views import reports
from core.views import directions
from core.views import rest

app_name = 'core'

urlpatterns = [
    path('', index.Index.as_view(), name='index'),

    path('user/', user.Search.as_view(), name='user'),
    path('user/add/', user.Edit.as_view(), name='user_add'),
    path('user/<int:pk>/', user.Edit.as_view(), name='user_edit'),
    path('user/<int:pk>/delete/', user.Delete.as_view(), name='user_delete'),

    path('reports/workers_done_report/', reports.WorkersDoneReport.as_view(), name='workers_done_report'),

    path('directions/', directions.Search.as_view(), name='direction_list'),

    path('rest/orgs/', rest.Orgs.as_view(), name='rest_orgs'),
]
