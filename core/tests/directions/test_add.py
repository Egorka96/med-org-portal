import datetime
import json
from unittest import mock

import core.forms
from core import models
from core.tests.base import BaseTestCase
from mis.pay_method import PayMethod
from requests import Response
from django.conf import settings



class TestCreate(BaseTestCase):
    view = 'core:direction_add'
    permission = 'core.add_direction'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

    @mock.patch.object(PayMethod, 'filter')
    def setUp(self, mock_request):
        mock_request.return_value = []
        super().setUp()

    def get_params(self):
        return {
            'last_name': 'Яковлев',
            'first_name': 'Иван',
            'middle_name': 'Михайлович',
            'birth': '23.02.2021',
            'exam_type': 'Периодический',
            'org': '',
            'orgs': [],
            'law_items_section_1': [],
            'law_items_section_2': [],
            'pay_method': '',
            'gender': '',
            'post': '',
            'shop': '',
            'order_types': [2],
            'date_from': datetime.date.today().strftime('%d.%m.%Y'),
            'date_to': '31.12.2021'
        }

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.post')
    @mock.patch.object(PayMethod, 'filter')
    def test_create(self, mock_request_pay_method, mock_request):
        params = self.get_params()
        response_json = {'id': 1}
        mock_request_pay_method.return_value = []
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=201)
        response = self.client.post(self.get_url(), params)

        expect_params = {
            'data': params ,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }

        m = mock_request.call_args_list[0].kwargs
        m['data']['date_to'] = m['data']['date_to'].strftime('%d.%m.%Y')
        m['data']['date_from'] = m['data']['date_from'].strftime('%d.%m.%Y')
        m['data']['birth'] = m['data']['birth'].strftime('%d.%m.%Y')
        self.assertEqual (expect_params, m)

    @mock.patch('requests.post')
    @mock.patch.object(core.forms, 'MisPayMethod')
    def test_create(self, mock_request_pay_method, mock_request):
        response_json = {
            'id': 1,
            'error': 'test_error'
        }
        params = self.get_params()
        params['pay_method'] = 1
        mock_request_pay_method.return_value = [('', '----------'), (1, 'test'), (2, 'test2')]

        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=400)
        response = self.client.post(self.get_url(), params)

        self.assertEqual(
            response.context['messages']._loaded_data[0].message,
            f'Ошибка создания направления: {response_json["error"]}'
        )

