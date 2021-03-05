import datetime
from unittest import mock

from core import models
from core.tests.base import BaseTestCase
from mis.direction import Direction
from requests import Response


class TestPrint(BaseTestCase):
    view = 'core:direction_print'
    permission = 'core.view_direction'
    direction_number = 1
    MIS_URL = 'http://127.0.0.1:8000'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

    @mock.patch.object(Direction, 'get')
    def setUp(self, mock_request_direction):
        mock_request_direction.return_value = Direction(
            number=1,
            last_name='Иван',
            first_name='Яковлев',
            gender='М',
            birth=datetime.date.today(),
            law_items_section_1=[],
            law_items_section_2=[]
        )
        super().setUp()

    def get_url_kwargs(self):
        return {'number': self.direction_number}

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch.object(Direction, 'get')
    def test_get(self, mock_request_direction):
        mock_request_direction.return_value = Direction(
            number=1,
            last_name='Иван',
            first_name='Яковлев',
            gender='М',
            birth=datetime.date.today(),
            law_items_section_1=[],
            law_items_section_2=[]
        )
        response = self.client.get(self.get_url())

        self.assertIn('application/vnd.openxmlformats-officedocument.wordprocessingml.document', response._content_type_for_repr)