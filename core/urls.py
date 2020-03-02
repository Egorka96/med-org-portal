from django.urls import path

from core import views
from core.views import user

app_name = 'core'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),

    path('user/', user.Search.as_view(), name='user'),
    path('user/add/', user.Edit.as_view(), name='user_add'),
    path('user/<int:pk>/', user.Edit.as_view(), name='user_edit'),
    path('user/<int:pk>/delete/', user.Delete.as_view(), name='user_delete'),
]
