import json
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from requests import Response

from core import models
from mis.service_client import Mis

User = get_user_model()


class TestMis(TestCase):
    MIS_URL = 'http://127.0.0.1:8000'

    def setUp(self):
        self.generate_data()

    def generate_data(self):
        self.user = User.objects.create(
            username='test',
            password='test',
        )
        self.core_user = models.User.objects.create(django_user=self.user, org_ids=json.dumps([1, 5]))

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.get')
    @override_settings(MIS_URL=MIS_URL)
    def test_get_status(self, mock_request):
        response_json = {'med_center': 1, 'is_out_used': True}
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        self.assertEqual(response_json, Mis().get_status())

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_request(self, mock_request):
        # произвольный ожидаемый ответ
        response_json = {'order_ids': [1, 2, 5, 8], 'user': 'test_user'}
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        path = '/api/orders/'
        self.assertEqual(response_json, Mis().request(path=path))

        expect_params = {
            'method': 'get',
            'url': self.MIS_URL + path,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'params': None,
            'data': None,
        }

        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_request_with_user(self, mock_request):
        # произвольный ожидаемый ответ
        response_json = {'order_ids': [1, 2, 5, 8], 'user': 'test_user'}
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        path = '/api/orders/'
        self.assertEqual(response_json, Mis().request(path=path, user=self.user))

        expect_params = {
            'method': 'get',
            'url': self.MIS_URL + path,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'params': {'orgs': json.loads(self.user.core.org_ids)},
            'data': None,
        }

        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)
