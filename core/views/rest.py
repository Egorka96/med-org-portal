import dataclasses
import json
from copy import copy

from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from swutils.date import date_to_rus

from core.datatools.password import create_password
from core import serializers, models
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

        orgs_data = Org.filter_raw(params=filter_params)
        return Response(orgs_data)


class LawItems(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        filter_params = copy(self.request.GET)
        filter_params['name'] = filter_params.getlist('term')

        law_items = LawItem.filter_raw(params=filter_params)
        return Response(law_items)


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

        worker = serializer.validated_data['worker']
        worker_mis_ids = worker.worker_orgs.all().values_list('mis_id', flat=True)

        documents = []
        for worker_mis_id in worker_mis_ids:
            worker_mis = Worker.get(worker_id=worker_mis_id, user=self.request.user)
            worker_documents = sorted(worker_mis.documents or [], key=lambda d: d.date, reverse=True)

            for document in worker_documents:
                document_dict = dataclasses.asdict(document)
                document_dict['date'] = date_to_rus(document.date)
                documents.append(document_dict)

        return Response({'worker_id': worker.id, 'documents': documents})


class GeneratePasswordView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({'password': create_password()})

