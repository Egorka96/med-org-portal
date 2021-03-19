import dataclasses
import datetime
from unittest import mock

from core.datatools.string import random_word
from core.tests.base import BaseRestTestCase
from django.urls import reverse
from mis.document import Document, DocumentType
from mis.org import Org
from mis.worker import Worker
from rest_framework.test import APITestCase
from djutils.date_utils import iso_to_date
from swutils.date import date_to_rus


class TestWorkerDocuments(BaseRestTestCase, APITestCase):
    permission = 'core.view_worker'

    def generate_data(self):
        super().generate_data()
        self.url = reverse('core:rest_worker_documents')

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
            last_name='Хищенко',
            first_name='Влад',
            middle_name='Андреевич',
            birth=datetime.date(2001, 11, 6),
            gender='Мужчина',
            org=[],
            post='',
            shop='',
            law_items_section_1=[],
            law_items_section_2=[],
            documents=worker_documents
        )


    @mock.patch.object(Worker, 'get')
    def test_worker_documents(self, mock_worker_documents):
        mock_worker_documents.return_value = self.get_mocked_worker_documents()

        params = {'worker_mis_id': 123 }
        response = self.client.get(self.url, params)

        self.assertEqual(response.status_code, 200)

        result_params = mock_worker_documents.return_value.documents
        serialized_documents = []
        for document in result_params:
            document_dict = dataclasses.asdict(document)
            document_dict['date'] = date_to_rus(document.date)
            serialized_documents.append(document_dict)

        self.assertEqual(serialized_documents[0], response.data['documents'][1])




