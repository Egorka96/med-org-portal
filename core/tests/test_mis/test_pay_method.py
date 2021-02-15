from unittest import mock


from django.test import TestCase, override_settings
from mis.pay_method import PayMethod
from rest_framework.utils import json
from requests import Response
from project import settings


class PayMethodTests(TestCase):
    MIS_URL = 'http://127.0.0.1:8000'

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.get')
    @override_settings(MIS_URL=MIS_URL)
    def test_filter(self, mock_request):
        response_json = [{
                'id': 1,
                'name': 'Наличные',
                'type': 'Наличные'
            },
            {
                'id': 2,
                'name': 'Безналичные',
                'type': 'Наличные'
            },
            {
                'id': 3,
                'name': 'Безналичные',
                'type': 'Безналичные'
        }]
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        pay_methods = []
        for item in response_json:
            pay_methods.append(PayMethod(
                id=item['id'],
                name=item['name'],
                type=item['type'],
            ))

        expect_params = {
            'url': self.MIS_URL + f'/api/pay_methods/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }

        pay_method = PayMethod.filter()
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)
        self.assertEqual(pay_methods, pay_method)
