import dataclasses
import datetime
from unittest import mock

from core import models
from core.datatools.string import random_word
from mis.document import Document, DocumentType
from mis.org import Org
from mis.worker import Worker
from swutils.date import date_to_rus
from core.tests.base import BaseRestTestCase
from django.urls import reverse
from rest_framework.test import APITestCase


class TestWorkerDocuments(BaseRestTestCase, APITestCase):
    permission = 'core.view_workers_document'

    def generate_data(self):
        super().generate_data()
        self.url = reverse('core:rest_worker_documents')
        self.worker = models.Worker.objects.create(
            id=1,
            last_name='Тестов',
            first_name='Тест',
            middle_name='Тестович',
            gender='Мужчина',
            birth=datetime.date(2001, 11, 6)
        )
        models.WorkerOrganization.objects.create(
            id=1,
            worker=self.worker,
            mis_id=1,
            org_id=1,
            post=''
        )

    def get_mocked_worker_documents(self):
        worker_documents  = []
        for i in range(2):
            document_type = DocumentType(
                id=i,
                name=random_word(10)
            )
            document = Document(
                date=datetime.date(2001, i+1, 12),
                document_type=document_type,
                document_link=random_word(10)
            )
            worker_documents.append(document)
        return Worker(
            id=1,
            last_name='Тестов',
            first_name='Тест',
            middle_name='Тестович',
            birth=datetime.date(2001, 11, 6),
            gender='Мужчина',
            org=Org(id=1, name='test'),
            post='',
            shop='',
            law_items=[],
            documents=worker_documents
        )

    @mock.patch.object(Worker, 'get')
    def test_worker_documents(self, mock_worker_documents):
        mock_worker_documents.return_value = self.get_mocked_worker_documents()

        params = {'worker': self.worker.id}
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, 200)

        result_params = mock_worker_documents.return_value.documents
        serialized_documents = []
        for document in result_params:
            document_dict = dataclasses.asdict(document)
            document_dict['date'] = date_to_rus(document.date)
            serialized_documents.append(document_dict)

        self.assertEqual(serialized_documents[0], response.data['documents'][1])

