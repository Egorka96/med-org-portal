import datetime
from unittest import mock

from core import models
from core.tests.base import BaseTestCase
from mis.service_client import Mis
from requests import Response


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
                        "display":"3.4.2 прил.1"
                    },
                    {
                        "id":602,
                        "name":"3.5",
                        "section":"1",
                        "description":"Производственный шум на рабочих местах с вредными и (или) опасными условиями труда, на которых имеется технологическое оборудование, являющееся источником шума.",
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
        self.assertEqual(response.context_data['object_list'], mock_request.return_value['results'])
        initial =  {
            'date_from': datetime.date.today()
        }
        self.assertEqual(response.context_data['form'].initial, initial)

    @mock.patch.object(Mis, 'request')
    def test_get_filter_params(self, mock_request):
        mock_request.return_value = self.get_result_mis()
        params = self.get_params()
        response = self.client.get(self.get_url(), params)

        self.assertEqual(response.context_data['object_list'], mock_request.return_value['results'])

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



