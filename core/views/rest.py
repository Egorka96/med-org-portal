import dataclasses
import json
from copy import copy

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from swutils.date import date_to_rus

from core.datatools.password import create_password
from core import serializers
from mis.law_item import LawItem
from mis.org import Org
from mis.worker import Worker


class ViewWorkerPermission(BasePermission):
    message = 'Просмотр сотрудника не разрешен'

    def has_permission(self, request, view):
        return request.user.has_perm('core.view_worker')


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

        law_items = LawItem.filter(params={'name': filter_params.get('term'), 'section': filter_params.get('section')})
        results = [
            {'id': l_i.id, 'text': l_i.name} for l_i in law_items
        ]

        return Response({'results': results})


class Workers(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        filter_params = copy(self.request.GET)

        workers = Worker.filter(params=filter_params, user=self.request.user)
        workers_dict = [dataclasses.asdict(w) for w in workers]
        for w in workers_dict:
            w['birth_rus'] = date_to_rus(w['birth'])
        return Response({'results': workers_dict})


class WorkerDocuments(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (ViewWorkerPermission, )

    def get(self, request, *args, **kwargs):
        serializer = serializers.WorkerDocuments(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        worker = Worker.get(worker_id=serializer.validated_data['worker_mis_id'], user=self.request.user)
        documents_by_date = worker.get_documents_by_dates()

        serialized_documents_by_dates = {}
        for date, documents in documents_by_date.items():
            serialized_documents_by_dates[date_to_rus(date)] = [dataclasses.asdict(document) for document in documents]

        return Response({'documents': dict(reversed(list(serialized_documents_by_dates.items())))})


class GeneratePasswordView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({'password': create_password()})

