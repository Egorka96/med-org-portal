from django.urls import path

from core.views import index
from core.views import user
from core.views import rest

app_name = 'core'

urlpatterns = [
    path('', index.Index.as_view(), name='index'),

    path('user/', user.Search.as_view(), name='user'),
    path('user/add/', user.Edit.as_view(), name='user_add'),
    path('user/<int:pk>/', user.Edit.as_view(), name='user_edit'),
    path('user/<int:pk>/delete/', user.Delete.as_view(), name='user_delete'),

    path('rest/orgs/', rest.Orgs.as_view(), name='rest_orgs')
]
