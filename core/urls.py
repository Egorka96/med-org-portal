from django.urls import path

from core.views import index
from core.views import user
from core.views import worker
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

    path('workers/', worker.Search.as_view(), name='workers'),
    path('workers/documents/print/', worker.DocumentPrint.as_view(), name='worker_documents_print'),

    path('reports/workers_done_report/', reports.WorkersDoneReport.as_view(), name='workers_done_report'),

    path('directions/', directions.Search.as_view(), name='direction_list'),
    path('directions/add/', directions.Edit.as_view(), name='direction_add'),
    path('directions/<int:number>/', directions.Edit.as_view(), name='direction_edit'),
    path('directions/<int:number>/delete/', directions.Delete.as_view(), name='direction_delete'),
    path('directions/<int:number>/print/', directions.Print.as_view(), name='direction_print'),

    path('rest/orgs/', rest.Orgs.as_view(), name='rest_orgs'),
    path('rest/workers/', rest.Workers.as_view(), name='rest_workers'),
    path('rest/worker_documents/', rest.WorkerDocuments.as_view(), name='rest_worker_documents'),
    path('rest/law_items/', rest.LawItems.as_view(), name='rest_law_items'),
    path('rest/generate_password/', rest.GeneratePasswordView.as_view(), name='rest_generate_password'),

    path('password_change/', user.PasswordChange.as_view(), name='password_change'),
    path('password_forgot/', user.PasswordForgot.as_view(), name='password_forgot')
]
