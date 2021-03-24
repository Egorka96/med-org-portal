import datetime
from unittest import mock
import os

from core import models
from core.tests.base import BaseTestCase
from mis.direction import Direction
from mis.law_item import LawItem, Law
from mis.org import Org
from mis.service_client import Mis
from requests import Response
from openpyxl import load_workbook
from swutils.date import date_to_rus
from djutils.date_utils import iso_to_date
import dataclasses


class TestSearch(BaseTestCase):
    view = 'core:direction_list'
    permission = 'core.view_direction'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

    @mock.patch.object(Mis, 'request')
    def setUp(self, mock_request):
        mock_request.return_value = self.get_result_mis()
        super().setUp()

    def get_result_mis(self):
        return {
            "count": 5,
            "next": None,
            "previous": None,
            "results":[{
                "id":17719,
                "last_name":"Тестов",
                "first_name":"Тест",
                "middle_name":"Тестович",
                "birth":"1982-11-14",
                "gender":"Мужской",
                "date_from":"2021-02-20",
                "date_to":"2021-12-31",
                "order_types":[{
                    "id":2,"label":"ПРОФ"
                }],
                "med_center":None,
                "org":{
                    "id":908,
                    "legal_name":"ООО \"Тестовая организация\""
                },
                "law_items":[
                    {
                        "id":601,
                        "name":"3.4.2",
                        "section":"1",
                        "description":"Общая вибрация ",
                         "law": {
                            "id": 5,
                            "name": "29н"
                        },
                        "display":"3.4.2 прил.1"
                    },
                    {
                        "id":602,
                        "name":"3.5",
                        "section":"1",
                        "description":"Производственный шум на рабочих местах с вредными и (или) опасными условиями труда, на которых имеется технологическое оборудование, являющееся источником шума.",
                         "law": {
                            "id": 5,
                            "name": "29н"
                        },
                        "display":"3.5 прил.1"
                    },
                ],
                "pay_method": {
                    "id":3,
                    "name":"Организация",
                    "type":"Организация",
                    "sort_priority":5.0
                },
                "exam_type":"Периодический",
                "post":"Тестировщик",
                "shop":"Тест",
                "confirm_dt":None
            }]
        }

    def get_params(self):
        return {
            'confirmed': '',
            'date_from': '',
            'date_to': '',
            'first_name': '',
            'last_name': 'Тестов',
            'middle_name': '',
            'org': '',
            'orgs': [],
            'per_page': '50',
            'post': '',
            'shop': ''
        }

    @mock.patch.object(Mis, 'request')
    def test_get_initial(self, mock_request):
        mock_request.return_value = self.get_result_mis()
        response = self.client.get(self.get_url())
        directions_expected = []
        for item in mock_request.return_value['results']:
            direction = Direction(
                number=item['id'],
                last_name=item['last_name'],
                first_name=item['first_name'],
                middle_name=item['middle_name'],
                birth=iso_to_date(item['birth']),
                gender=item['gender'],
                from_date=iso_to_date(item['date_from']),
                to_date=iso_to_date(item['date_to']),
                org=Org.get_from_dict(data=item['org']) if item.get('org') else None,
                pay_method=item['pay_method'],
                exam_type=item['exam_type'],
                post=item['post'],
                shop=item['shop'],
                law_items=[LawItem.get_from_dict(l_i) for l_i in item.get('law_items', [])],
                confirm_date=iso_to_date(item['confirm_dt']),
            )
            directions_expected.append(direction)

        self.assertEqual(response.context_data['object_list'], directions_expected)

        initial =  {
            'date_from': datetime.date.today()
        }
        self.assertEqual(response.context_data['form'].initial, initial)

    @mock.patch.object(Mis, 'request')
    def test_get_filter_params(self, mock_request):
        mock_request.return_value = self.get_result_mis()

        params = self.get_params()
        response = self.client.get(self.get_url(), params)
        directions_expected = []
        for item in mock_request.return_value['results']:
            direction = Direction(
                number=item['id'],
                last_name=item['last_name'],
                first_name=item['first_name'],
                middle_name=item['middle_name'],
                birth=iso_to_date(item['birth']),
                gender=item['gender'],
                from_date=iso_to_date(item['date_from']),
                to_date=iso_to_date(item['date_to']),
                org=Org.get_from_dict(data=item['org']) if item.get('org') else None,
                pay_method=item['pay_method'],
                exam_type=item['exam_type'],
                post=item['post'],
                shop=item['shop'],
                law_items=[LawItem.get_from_dict(l_i) for l_i in item.get('law_items', [])],
                confirm_date=iso_to_date(item['confirm_dt']),
            )
            directions_expected.append(direction)

        self.assertEqual(response.context_data['object_list'], directions_expected)

        params['confirmed'] = None
        params['date_from'] = None
        params['date_to'] = None
        expect_params = {
            'path': '/api/pre_record/',
            'user': self.core_user,
            'params': params
        }

        mock_params = mock_request.call_args_list[0].kwargs
        mock_params['user'] = mock_params['user'].core
        self.assertEqual(expect_params, mock_params)

    @mock.patch.object(Mis, 'request')
    def test_excel(self, mock_request):
        mock_request.return_value = self.get_result_mis()

        params = self.get_params()
        params['excel'] = 1
        response = self.client.get(self.get_url(), params)

        self.assertIn('application/ms-excel', response._content_type_for_repr)

        filepath = 'core/tests/test_directions/test.xlsx'
        with open(filepath, 'wb') as file:
            file.write(response.content)
        wb = load_workbook(filename=filepath)

        result_expected_dict = {
            'number': 1,
            'fio': 'Тестов Тест Тестович',
            'birth': '14.11.1982',
            'gender':'Мужской',
            'org': "ООО \"Тестовая организация\"",
            'post': 'Тестировщик',
            'shop': 'Тест',
            'exam_type': 'Периодический',
            'law_items': '3.4.2, 3.5',
            'date': 'с 20.02.2021 по 31.12.2021',
            'confirm_dt': '-'
        }
        result_expected = list(result_expected_dict.values())
        result_excel = [c.value for c in wb.worksheets[0][3]][:11]

        self.assertEqual(result_excel, result_expected)

        title_list = ['№', 'ФИО', 'Дата рождения', 'Пол', 'Организация', 'Должность', 'Подразделение', 'Вид осмотра',
                      'Пункты приказа', 'Время действия', 'Дата прохождения']
        result_excel_title = [c.value for c in wb.worksheets[0][2]]

        self.assertEqual(result_excel_title, title_list)

        header_list = ['Направления']
        result_excel_header = [c.value for c in wb.worksheets[0][1][:1]]

        self.assertEqual(result_excel_header, header_list)
        os.remove(filepath)



