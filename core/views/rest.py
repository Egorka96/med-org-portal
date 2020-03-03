from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mis.org import Org


class Orgs(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        orgs = Org.filter(params=self.request.GET)

        results = [
            {'id': org.id, 'text': org.name} for org in orgs
        ]

        return Response({'results': results})
