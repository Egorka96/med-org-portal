import dataclasses
import json
from copy import copy

from django.http import HttpResponse
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from swutils.date import date_to_rus
from swutils.string import transliterate

import help.article
from core.datatools.password import create_password
from core import serializers, models
from mis.law_item import LawItem
from mis.org import Org
from mis.worker import Worker
from mis.document import Document


class ViewWorkerDocumentPermission(BasePermission):
    message = 'Просмотр документов сотрудника не разрешен'

    def has_permission(self, request, view):
        return request.user.has_perm('core.view_workers_document')


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


class DocumentsChoices(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (ViewWorkerDocumentPermission, )

    def get(self, request, *args, **kwargs):
        serializer = serializers.Documents(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        choices = Document.get_choices(serializer.validated_data['search_params'])

        results = []
        available_doc_type_ids = self.request.user.core.available_document_type_ids.\
            values_list('document_type_id', flat=True)
        for item in choices:
            if item['doc_type'].id not in available_doc_type_ids:
                continue

            item['doc_type'] = dataclasses.asdict(item['doc_type'])
            results.append(item)

        return Response(results)


class DocumentPrint(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (ViewWorkerDocumentPermission,)

    def get(self, request, *args, **kwargs):
        serializer = serializers.DocumentPrint(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        file_name = transliterate(serializer.validated_data['name']).replace('"', '').replace("'", '')
        pdf_content = Document.get_content(path=serializer.validated_data['link'])

        # сгенерируем HttpResponse-объект с pdf
        response = HttpResponse(pdf_content, content_type="application/pdf")
        response['Content-Disposition'] = f'filename={file_name}.pdf'
        return response


class WorkerDocuments(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (ViewWorkerDocumentPermission, )

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
