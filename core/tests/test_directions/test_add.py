import datetime
import json
from unittest import mock
from requests import Response

from django.conf import settings
from djutils.date_utils import rus_to_date

from core import forms
from core.tests.base import BaseTestCase

from mis.law_item import Law
from mis.pay_method import PayMethod

class TestCreate(BaseTestCase):
    view = 'core:direction_add'
    permission = 'core.add_direction'

    @mock.patch.object(PayMethod, 'filter')
    @mock.patch.object(Law, 'filter')
    def setUp(self, mock_law, mock_request):
        mock_request.return_value = []
        mock_law.return_value = [Law(id=1, name='29н')]
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
            'law_items': [],
            'law_items_29': [],
            'law_items_302_section_1': [],
            'law_items_302_section_2': [],
            'pay_method': '',
            'gender': '',
            'post': '',
            'shop': '',
            'order_types': [2],
        }

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.post')
    @mock.patch.object(PayMethod, 'filter')
    @mock.patch.object(Law, 'filter')
    def test_create(self, mock_law, mock_request_pay_method, mock_request):
        params = self.get_params()
        response_json = {'id': 1}
        mock_request_pay_method.return_value = []
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=201)
        mock_law.return_value = [Law(id=1, name='29н')]

        params = {key: value for key, value in params.items() if value}
        response = self.client.post(self.get_url(), params)
        params['date_from'] = datetime.date.today()
        params['date_to'] = datetime.date(params['date_from'].year, 12, 31).isoformat()
        params['date_from'] = datetime.date.today().isoformat()
        params['birth'] = rus_to_date(params['birth']).isoformat()
        expect_params = {
            'json': params ,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }

        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.post')
    @mock.patch.object(forms, 'MisPayMethod')
    @mock.patch.object(Law, 'filter')
    def test_form_invalid(self, mock_law, mock_request_pay_method, mock_request):
        response_json = {
            'id': 1,
            'error': 'test_error'
        }
        params = self.get_params()
        params['pay_method'] = 1
        mock_request_pay_method.return_value = [('', '----------'), (1, 'test'), (2, 'test2')]
        mock_law.return_value = [Law(id=1, name='29н')]

        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=400)
        response = self.client.post(self.get_url(), params)

        self.assertEqual(
            response.context['messages']._loaded_data[0].message,
            f'Ошибка создания направления: {response_json["error"]}'
        )

