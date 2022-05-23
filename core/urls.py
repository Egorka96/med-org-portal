from django.urls import path

from core.views import index, login
from core.views import user
from core.views import worker
from core.views import reports
from core.views import directions
from core.views import log
from core.views import rest

app_name = 'core'

urlpatterns = [
    path('', index.Index.as_view(), name='index'),

    path('user/', user.Search.as_view(), name='user'),
    path('user/add/', user.Edit.as_view(), name='user_add'),
    path('user/<int:pk>/', user.Edit.as_view(), name='user_edit'),
    path('user/<int:pk>/delete/', user.Delete.as_view(), name='user_delete'),

    path('workers/', worker.Search.as_view(), name='workers'),
    path('reports/workers_done_report/', reports.WorkersDoneReport.as_view(), name='workers_done_report'),

    path('log/', log.Log.as_view(), name='log'),

    path('directions/', directions.Search.as_view(), name='direction_list'),
    path('directions/add/', directions.Edit.as_view(), name='direction_add'),
    path('directions/<int:number>/', directions.Edit.as_view(), name='direction_edit'),
    path('directions/<int:number>/delete/', directions.Delete.as_view(), name='direction_delete'),
    path('directions/<int:number>/print/', directions.Print.as_view(), name='direction_print'),

    path('rest/orgs/', rest.Orgs.as_view(), name='rest_orgs'),
    path('rest/workers/', rest.Workers.as_view(), name='rest_workers'),
    path('rest/documents/choices/', rest.DocumentsChoices.as_view(), name='rest_documents_choices'),
    path('rest/documents/print/', rest.DocumentPrint.as_view(), name='rest_documents_print'),
    path('rest/worker_documents/', rest.WorkerDocuments.as_view(), name='rest_worker_documents'),
    path('rest/law_items/', rest.LawItems.as_view(), name='rest_law_items'),
    path('rest/generate_password/', rest.GeneratePasswordView.as_view(), name='rest_generate_password'),

    path('password_change_required/', login.PasswordChangeRequired.as_view(), name='password_change_required'),
    path('password_forgot/', login.PasswordForgot.as_view(), name='password_forgot'),
]
