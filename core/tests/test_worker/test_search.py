import datetime
from unittest import mock

from core import models
from core.tests.base import BaseTestCase
from djutils.date_utils import iso_to_date
from mis.org import Org
from mis.service_client import Mis
from mis.worker import Worker


class TestsSearch(BaseTestCase):
    view = 'core:workers'
    permission = 'core.view_worker'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

    @mock.patch.object(Mis, 'request')
    def setUp(self, mock_request):
        mock_request.return_value = self.get_result_mis()
        super().setUp()

    def get_result_mis(self):
        return {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [{
                "id": 4937,
                "org": {
                    "id": 449,
                    "name": "Тестовая организация 449",
                    "legal_name": "ООО \"Тестовая организация\"",
                    "inn": "",
                    "legal_address": "",
                    "actual_address": ""
                },
                "law_items": [],
                "last_name": "Яковлев",
                "first_name": "Евгений",
                "middle_name": "Владимирович",
                "slug_name": "20011775ев",
                "birth": "1995-03-13",
                "gender": "Мужской",
                "snils": "",
                "start_work_date": None,
                "end_work_date": None,
                "end_work_decree": "",
                "post": "",
                "shop": "Кофейня",
                "department": None
                }]
            }

    def get_params(self):
        return {
            'first_name': ['Евгений'],
            'last_name': ['Яковлев'],
            'middle_name': ['Владимирович'],
            'per_page': '100'
        }

    @mock.patch.object(Mis, 'request')
    def test_search(self, mock_request):
        mock_request.return_value = self.get_result_mis()
        params = self.get_params()

        response = self.client.get(self.get_url(), params)
        expect_params = {
            'path': '/api/workers/',
            'user': self.core_user,
            'params': params
        }

        mock_params = mock_request.call_args_list[0].kwargs
        mock_params['user'] = mock_params['user'].core
        self.assertEqual(expect_params, mock_params)

        workers = []
        for worker_data in mock_request.return_value['results']:
            org = Org(
                id=worker_data['org']['id'],
                name=worker_data['org']['name'],
                legal_name=worker_data['org']['legal_name']
            )
            workers.append(Worker(
                id=worker_data['id'],
                last_name=worker_data['last_name'],
                first_name=worker_data['first_name'],
                middle_name=worker_data['middle_name'],
                birth=iso_to_date(worker_data['birth']),
                gender=worker_data['gender'],
                org=org,
                post=worker_data['post'],
                shop=worker_data['shop'],
                law_items_section_1=[],
                law_items_section_2=[],
                documents=None
            ))

        self.assertEqual(workers, response.context_data['object_list'])





