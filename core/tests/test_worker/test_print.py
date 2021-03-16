import datetime
import json
from unittest import mock

from core.tests.base import BaseTestCase
from mis.document import Document
from mis.org import Org
from mis.service_client import Mis
from mis.worker import Worker
from requests import Response
from project import settings


class TestsDocumentPrint(BaseTestCase):
    view = 'core:worker_documents_print'
    permission = 'core.view_worker'

    @mock.patch.object(Worker, 'get')
    @mock.patch.object(Document, 'get_content')
    def test_print(self, mock_request, mock_request_worker):
        # response_json = self.get_result_mis()
        org = Org(
            id=1,
            name='Тестовая организация 449',
            legal_name=''
        )
        mock_request_worker.return_value = Worker(
            id=1,
            org=org,
            last_name='Белко',
            first_name='Макс',
            birth=datetime.date(2003, 3, 31),
            gender='Мужчина'
        )
        with open('%s/core/tests/test_worker/test.txt' % settings.BASE_DIR, mode='rb') as file:
            mock_request.return_value = file.read()

        params = {
            'worker_mis_id': 1,
            'document_link': '/path/mis/'
        }
        response = self.client.get(self.get_url(), params)
        self.assertIn('application/pdf', response._content_type_for_repr)




