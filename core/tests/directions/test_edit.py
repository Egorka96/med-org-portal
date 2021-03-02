import datetime
import json
from unittest import mock

import core.forms
from core import models
from mis.pay_method import PayMethod
from core.tests.base import BaseTestCase
from mis.direction import Direction
from requests import Response


class TestEdit(BaseTestCase):
    view = 'core:direction_edit'
    permission = 'core.change_direction'
    direction_number = 1

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

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

    def get_mis(self):
        return {
            'id':1,
            'last_name': 'Яковлев',
            'first_name': 'Иван',
            'middle_name': 'Михайлович',
            'birth': datetime.date.today().isoformat(),
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
            # 'order_types': [2],
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
                    "display":"3.4.2 прил.1"
                },
                {
                    "id":602,
                    "name":"3.5",
                    "section":"2",
                    "description":"Производственный шум на рабочих местах с вредными и (или) опасными условиями труда, на которых имеется технологическое оборудование, являющееся источником шума.",
                    "display":"3.5 прил.1"
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

    @mock.patch('requests.request')
    @mock.patch.object(core.forms, 'MisPayMethod')
    @mock.patch.object(core.forms, 'LawItem')
    @mock.patch.object(core.forms, 'Org')
    def test_get_initial(self, mock_request_org, mock_request_law_items, mock_request_pay_method, mock_request):
        mock_request_org.return_value = [(908, 'test')]
        mock_request_law_items.return_value = [(601, 'test'), (602, 'test2')]
        mock_request_pay_method.return_value = [('', '----------'), (1, 'test'), (2, 'test2')]
        mock_request.return_value = self.get_response(content=json.dumps(self.get_mis()))

        response = self.client.post(self.get_url())
        get_mis = self.get_mis()
        expect_params = {
            'last_name': get_mis['last_name'],
            'first_name': get_mis['first_name'],
            'middle_name': get_mis['middle_name'],
            'birth': datetime.datetime.strptime('2021-03-02', "%Y-%m-%d").date(),
            'exam_type': get_mis['exam_type'],
            'pay_method': 1,
            'gender': get_mis['gender'],
            'post': get_mis['post'],
            'shop': get_mis['shop'],
            'org': get_mis['org']['id'],
            'law_items_section_1': [601],
            'law_items_section_2': [602],
            'confirm_date': datetime.date(2021, 10, 31),
            'from_date': datetime.date.today(),
            'to_date': datetime.date(2021, 12, 31),
            'number': 1
        }

        self.assertEqual(expect_params, response.context_data['form'].initial)
