from django.urls import path

from help.views import article

app_name = 'help'

urlpatterns = [
    path('rest/article/', article.ArticleView.as_view(), name='rest_article'),
]
