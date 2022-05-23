from copy import copy
from dataclasses import asdict


from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from help import article


class ArticleView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        filter_params = copy(self.request.GET)

        article_data = {}
        articles = []
        article_obj = article.Article.filter(params=filter_params)
        for item in article_obj:
            articles.append(asdict(item))
        article_data['results'] = articles

        return Response(article_data)