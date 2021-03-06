import datetime
import json
from unittest import mock

from core import models, consts
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

    def generate_data(self):
        super().generate_data()
        self.worker = models.Worker.objects.create(
            id=1,
            last_name='Хищенко',
            first_name='Влад',
            middle_name='Андреевич',
            gender=consts.MALE,
            birth=datetime.date(2001, 11, 6)
        )
        self.worker_org = models.WorkerOrganization.objects.create(
            id=1,
            worker=self.worker,
            mis_id=1,
            org_id=1,
            post=''
        )

    @mock.patch.object(Worker, 'get')
    @mock.patch.object(Document, 'get_content')
    def test_print(self, mock_request, mock_request_worker):
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
            gender=consts.MALE
        )
        with open('%s/core/tests/test_worker/test.txt' % settings.BASE_DIR, mode='rb') as file:
            mock_request.return_value = file.read()

        params = {
            'worker_id': self.worker_org.mis_id,
            'document_link': '/path/mis/'
        }
        response = self.client.get(self.get_url(), params)
        self.assertIn('application/pdf', response._content_type_for_repr)




