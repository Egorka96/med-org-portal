import json
import os
from unittest import mock

import core.forms
from core import models
from core.tests.base import BaseTestCase
from djutils.date_utils import iso_to_date
from requests import Response
from django.conf import settings
from openpyxl import Workbook, load_workbook
from swutils.date import date_to_rus


class TestWorkersDoneReport(BaseTestCase):
    view = 'core:workers_done_report'
    permission = 'core.view_workers_done_report'
    MIS_URL = 'http://127.0.0.1:8000'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.request')
    @mock.patch.object(core.forms.Mis, 'is_out_used')
    def setUp(self, mock_request_is_out_used, mock_request):
        mock_request.return_value = self.get_response(content=json.dumps(self.get_result_mis()))
        mock_request_is_out_used.return_value = True
        super().setUp()

    def get_result_mis(self):
        return {
            "count": 3,
            "next": None,
            "previous": None,
            "results": [{
                "client": {
                    "id": 123,
                    "last_name": "Тестов",
                    "first_name": "Тест",
                    "middle_name": "Тестович",
                    "fio": "Тестов Тест Тестович",
                    "gender": "Мужской",
                    "birth": "1956-07-09",
                    "phone": "",
                    "email": ""
                },
                "date": "2020-01-02",
                "dates": [
                    "2020-01-02"
                ],
                "certificate": [],
                "prof": [{
                    "id": 62747,
                    "number": 6040011249,
                    "date": "2020-01-02",
                    "app": "prof",
                    "med_center": {
                        "id": 4,
                        "actual_name": "Добрый Доктор",
                        "legal_name": "ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ \"Добрый Доктор\""
                    },
                    "org": {
                        "id": 123,
                        "name": "Тестовая организация",
                        "legal_name": "Тестовая организация"
                    },
                    "exam_type": "Предварительный",
                    "prof_conclusion": {
                        "conclusion": "Медицинские противопоказания к работе не выявлены",
                        "conclusion_dt": "2020-01-29T23:30:14.545767"
                    },
                    "law_items": [{
                        "id": 621,
                        "name": "15",
                        "section": "2",
                        "factors": "",
                    }],
                    "shop": "",
                    "main_services": "Предварительный ПРОФ осмотр"
                }],
                "lmk": [],
                "heal": [],
                "total_cost": 2000,
                "orgs": [{
                    "id": 123,
                    "name": "Тестовая организация",
                    "legal_name": "Тестовая организация"
                }],
                'posts': ''
            }]
        }

    def get_params(self):
        return {
            'confirmed': [''],
            'date_from': [''],
            'date_to': [''],
            'first_name': [''],
            'last_name': ['Тестов'],
            'middle_name': [''],
            'org': [''],
            'per_page': '50',
            'post': [''],
            'shop': [''],
            'group_clients': True
        }

    @mock.patch('requests.request')
    @mock.patch.object(core.forms.Mis, 'is_out_used')
    def test_object_list(self, mock_request_is_out_used, mock_request):
        mock_request_is_out_used.return_value = True
        mock_request.return_value = self.get_response(content=json.dumps(self.get_result_mis()))
        params = self.get_params()

        response = self.client.get(self.get_url(), params)
        result_response = self.get_result_mis()['results']
        result_response[0]['main_services'] = ['Предварительный ПРОФ осмотр']
        expect_params = {
            'url': '/api/orders/by_client_date/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'params': params,
            'method': 'get',
            'data': None
        }

        self.assertEqual(response.context_data['object_list'], result_response)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.request')
    @mock.patch.object(core.forms.Mis, 'is_out_used')
    def test_object_list_null(self, mock_request_is_out_used, mock_request):
        mock_request_is_out_used.return_value = True
        mock_request.return_value = self.get_response(content=json.dumps(self.get_result_mis()))

        response = self.client.get(self.get_url())

        self.assertFalse(response.context_data['object_list'])

    @mock.patch('requests.request')
    @mock.patch.object(core.forms.Mis, 'is_out_used')
    def test_excel(self, mock_request_is_out_used, mock_request):
        mock_request_is_out_used.return_value = True
        mock_request.return_value = self.get_response(content=json.dumps(self.get_result_mis()))

        params = self.get_params()
        params['excel'] = 1
        response = self.client.get(self.get_url(), params)

        self.assertIn('application/ms-excel' ,response._content_type_for_repr)

        with open('core/tests/test_reports/test.xlsx', 'wb') as file:
            file.write(response.content)

        response_json = self.get_result_mis()
        result_expected_dict = {
            'number': 1,
            'date': date_to_rus(iso_to_date(response_json['results'][0]['date'])),
            'fio': response_json['results'][0]['client']['fio'],
            'birth': date_to_rus(iso_to_date(response_json['results'][0]['client']['birth'])),
            'gender': response_json['results'][0]['client']['gender'],
            'shop': None,
            'post': None,
            'org': response_json['results'][0]['prof'][0]['org']['name'],
            'main_services': response_json['results'][0]['prof'][0]['main_services'],
            'law_items': '15 прил.2',
            'prof_conclusion': response_json['results'][0]['prof'][0]['prof_conclusion']['conclusion'],
        }
        result_expected = list(result_expected_dict.values())
        wb = load_workbook(filename = 'core/tests/test_reports/test.xlsx')
        result_excel = [c.value for c in wb.worksheets[0][3]][:11]

        self.assertEqual(result_excel, result_expected)

        title_list = ['№', 'Дата осмотра', 'ФИО', 'Дата рождения', 'Пол', 'Подразделение', 'Должность', 'Организация',
                      'Вид осмотра', 'Пункты приказа', 'Заключение профпатолога', 'Примечание']
        result_excel_title = [c.value for c in wb.worksheets[0][2]]

        self.assertEqual(result_excel_title, title_list)

        header_list = ['Отчет по прошедшим']
        result_excel_header = [c.value for c in wb.worksheets[0][1][:1]]

        self.assertEqual(result_excel_header, header_list)

        os.remove('core/tests/test_reports/test.xlsx')