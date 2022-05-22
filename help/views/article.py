import json
from copy import copy


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

        article_data = article.Article.filter_raw(params=filter_params)
        return Response(article_data)
