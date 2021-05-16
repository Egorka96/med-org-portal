import datetime
import json
from unittest import mock

import core.forms
from core import models
from django.test import override_settings
from mis.pay_method import PayMethod
from core.tests.base import BaseTestCase
from mis.direction import Direction
from requests import Response
from django.conf import settings


class TestEdit(BaseTestCase):
    view = 'core:direction_edit'
    permission = 'core.change_direction'
    direction_number = 1
    MIS_URL = 'http://127.0.0.1:8000'

    @mock.patch.object(PayMethod, 'filter')
    @mock.patch.object(Direction, 'get')
    def setUp(self, mock_request_direction, mock_request_pay_method):
        mock_request_pay_method.return_value = []
        mock_request_direction.return_value = Direction(
            number=1,
            last_name='Иван',
            first_name='Яковлев',
            gender='М',
            birth=datetime.date.today()
        )
        super().setUp()

    def get_result_mis(self):
        return {
            'id':1,
            'last_name': 'Иван',
            'first_name': 'Яковлев',
            'middle_name': 'Михайлович',
            'birth': datetime.date(2021, 3, 2).isoformat(),
            'exam_type': 'Периодический',
            'pay_method': {
                "id":1,
                "name":"Организация",
                "type":"Организация",
                "sort_priority":5.0,
            },
            'gender': '',
            'post': '',
            'shop': '',
            'date_from': datetime.date.today().isoformat(),
            'date_to': datetime.date(2021, 12, 31).isoformat(),
            'confirm_dt': datetime.date(2021, 10, 31).isoformat(),
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
                        "id": 1,
                        "name": "302н",
                    },
                },
                {
                    "id":602,
                    "name":"3.5",
                    "section":"2",
                    "description":"Производственный шум на рабочих местах с вредными и (или) опасными условиями труда, на которых имеется технологическое оборудование, являющееся источником шума.",
                    "law": {
                        "id": 1,
                        "name": "302н",
                    },
                },
            ],
        }

    def get_url_kwargs(self):
        return {'number': self.direction_number}

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    def get_params(self):
        return {
            'last_name': 'Василий',
            'first_name': 'Пупкин',
            'middle_name': self.get_result_mis()['middle_name'],
            'birth': '04.03.2001',
            'gender': '',
            'law_items_29': [],
            'law_items_302_section_1': [],
            'law_items_302_section_2': [],
            'exam_type': self.get_result_mis()['exam_type'],
            'law_items': [],
            'org': '',
            'orgs': [],
            'pay_method': '',
            'post': '',
            'shop': ''
        }

    @mock.patch('requests.request')
    @mock.patch.object(core.forms, 'MisPayMethod')
    @mock.patch.object(core.forms, 'LawItem')
    @mock.patch.object(core.forms, 'Org')
    def test_get_initial(self, mock_request_org, mock_request_law_items, mock_request_pay_method, mock_request):
        mock_request_org.return_value = [(908, 'test')]
        mock_request_law_items.return_value = [(601, 'test'), (602, 'test2')]
        mock_request_pay_method.return_value = [('', '----------'), (1, 'test'), (2, 'test2')]
        mock_request.return_value = self.get_response(content=json.dumps(self.get_result_mis()))

        response = self.client.post(self.get_url())
        result_mis = self.get_result_mis()
        expect_params = {
            'last_name': result_mis['last_name'],
            'first_name': result_mis['first_name'],
            'middle_name': result_mis['middle_name'],
            'birth': datetime.datetime.strptime('2021-03-02', "%Y-%m-%d").date(),
            'exam_type': result_mis['exam_type'],
            'pay_method': 1,
            'gender': result_mis['gender'],
            'post': result_mis['post'],
            'shop': result_mis['shop'],
            'org': result_mis['org']['id'],
            'law_items_302_section_1': [601],
            'law_items_302_section_2': [602],
            'law_items': result_mis['law_items'],
            'confirm_date': datetime.date(2021, 10, 31),
            'from_date': datetime.date.today(),
            'to_date': datetime.date(2021, 12, 31),
            'number': 1,
            'insurance_policy': None
        }

        self.assertEqual(expect_params, response.context_data['form'].initial)

    @mock.patch('requests.put')
    @mock.patch.object(core.forms, 'MisPayMethod')
    @mock.patch.object(core.forms, 'LawItem')
    @mock.patch.object(core.forms, 'Org')
    @mock.patch.object(Direction, 'get')
    @override_settings(MIS_URL=MIS_URL)
    def test_post(self, mock_request_direction, mock_request_org, mock_request_law_items, mock_request_pay_method, mock_request_put):
        result_mis = self.get_result_mis()
        response_json = {'id': 1}
        mock_request_put.return_value = self.get_response(content=json.dumps(response_json))
        mock_request_pay_method.return_value = []
        mock_request_law_items.return_value = [(601, 'test'), (602, 'test2')]
        mock_request_org.return_value = [(908, 'test')]
        mock_request_direction.return_value = Direction(
            number=result_mis['id'],
            last_name=result_mis['last_name'],
            first_name=result_mis['first_name'],
            middle_name=result_mis['middle_name'],
            birth=result_mis['birth'],
            gender=result_mis['gender'],
        )

        params = self.get_params()
        response = self.client.post(self.get_url(), params)
        params['order_types'] = [2]
        params['birth'] = datetime.date(2001, 3, 4).isoformat()
        params = {key: value for key, value in params.items() if value}
        expect_params = {
            'json': params ,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'url': self.MIS_URL + '/api/pre_record/1/'
        }

        self.assertEqual(response.status_code, 302)
        self.assertEqual(mock_request_put.call_args_list[0].kwargs, expect_params)

    @mock.patch('requests.put')
    @mock.patch.object(core.forms, 'MisPayMethod')
    @mock.patch.object(core.forms, 'LawItem')
    @mock.patch.object(core.forms, 'Org')
    @mock.patch.object(Direction, 'get')
    @override_settings(MIS_URL=MIS_URL)
    def test_post_confirm_date(self, mock_request_direction, mock_request_org, mock_request_law_items, mock_request_pay_method, mock_request_put):
        result_mis = self.get_result_mis()
        response_json = {'id': 1}
        mock_request_put.return_value = self.get_response(content=json.dumps(response_json))
        mock_request_pay_method.return_value = []
        mock_request_law_items.return_value = [(601, 'test'), (602, 'test2')]
        mock_request_org.return_value = [(908, 'test')]
        mock_request_direction.return_value = Direction(
            number=result_mis['id'],
            last_name=result_mis['last_name'],
            first_name=result_mis['first_name'],
            middle_name=result_mis['middle_name'],
            birth=result_mis['birth'],
            gender=result_mis['gender'],
            confirm_date=datetime.date(2021, 4, 3),
        )

        params = self.get_params()
        response = self.client.post(self.get_url(), params)

        self.assertEqual(
            response.context['messages']._loaded_data[0].message,
            'Редактирование направления запрещено: по нему уже создана заявка на осмотр в медицинской информационной системе'
        )



