import datetime
import json
from unittest import mock

from core.tests.base import BaseTestCase
from django.conf import settings
from django.test import override_settings
from mis.direction import Direction
from requests import Response


class TestDelete(BaseTestCase):
    view = 'core:direction_delete'
    permission = 'core.delete_direction'
    direction_number = 1
    MIS_URL = 'http://127.0.0.1:8000'

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch.object(Direction, 'get')
    def setUp(self, mock_request):
        mock_request.return_value = Direction(
            number=1,
            last_name='Иван',
            first_name='Яковлев',
            gender='М',
            birth=datetime.date.today()
        )
        super().setUp()

    def get_url_kwargs(self):
        return {'number': self.direction_number}

    @mock.patch('requests.delete')
    @override_settings(MIS_URL=MIS_URL)
    def test_delete(self, mock_request):
        response_json = {'id': self.direction_number}
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=204)

        response = self.client.delete(self.get_url())
        expect_params = {
            'url':  self.MIS_URL + f'/api/pre_record/{self.direction_number}/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }

        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch.object(Direction, 'get')
    @mock.patch('requests.delete')
    @override_settings(MIS_URL=MIS_URL)
    def test_delete_error(self, mock_request, mock_request_direction):
        response_json = {
            'id': self.direction_number,
            'error': 'test_error'
        }
        mock_request_direction.return_value = Direction(
            number=1,
            last_name='Иван',
            first_name='Яковлев',
            gender='М',
            birth=datetime.date.today() ,
        )
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=400)

        response = self.client.delete(self.get_url())

        self.assertEqual(
            response.context['messages']._loaded_data[0].message,
            f'Ошибка удаления направления: Ошибка запроса'
        )
