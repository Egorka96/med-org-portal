import json
from copy import copy

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mis.law_item import LawItem
from mis.org import Org


class Orgs(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        filter_params = copy(self.request.GET)

        if self.request.user.core.org_ids:
            filter_params.update({
                'id': json.loads(self.request.user.core.org_ids)
            })

        orgs = Org.filter(params=filter_params)
        results = [
            {'id': org.id, 'text': org.name} for org in orgs
        ]

        return Response({'results': results})


class LawItems(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        filter_params = copy(self.request.GET)

        law_items = LawItem.filter(params=filter_params)
        results = [
            {'id': l_i.id, 'text': l_i.name if filter_params.get('section') else str(l_i)} for l_i in law_items
        ]

        return Response({'results': results})
