import datetime
from unittest import mock

from core import models
from core.tests.base import BaseTestCase
from mis.direction import Direction
from mis.org import Org
from requests import Response


class TestPrint(BaseTestCase):
    view = 'core:direction_print'
    permission = 'core.view_direction'
    direction_number = 1
    MIS_URL = 'http://127.0.0.1:8000'

    @mock.patch.object(Org, 'get')
    @mock.patch.object(Direction, 'get')
    def setUp(self, mock_request_direction, mock_request_org):
        org = Org(
            id=1,
            name='Тест',
            legal_name='OOO Тест'
        )
        mock_request_org.return_value = org
        mock_request_direction.return_value = Direction(
            number=1,
            last_name='Иван',
            first_name='Яковлев',
            gender='М',
            birth=datetime.date.today(),
            law_items=[],
            org = org
        )
        super().setUp()

    def get_url_kwargs(self):
        return {'number': self.direction_number}

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch.object(Org, 'get')
    @mock.patch.object(Direction, 'get')
    def test_get(self, mock_request_direction, mock_request_org):
        org = Org(
            id=1,
            name='Тест',
            legal_name='OOO Тест'
        )
        mock_request_org.return_value = org
        mock_request_direction.return_value = Direction(
            number=1,
            last_name='Иван',
            first_name='Яковлев',
            gender='М',
            birth=datetime.date.today(),
            law_items=[],
            org=org
        )
        response = self.client.get(self.get_url())

        self.assertIn('application/vnd.openxmlformats-officedocument.wordprocessingml.document', response._content_type_for_repr)