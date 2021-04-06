import datetime
from unittest import mock

from core import models, consts
from core.tests.base import BaseTestCase
from djutils.date_utils import iso_to_date
from mis.org import Org
from mis.service_client import Mis
from mis.worker import Worker


class TestsSearch(BaseTestCase):
    view = 'core:workers'
    permission = 'core.view_worker'

    def generate_data(self):
        super().generate_data()
        self.core_user = models.User.objects.create(django_user=self.user)
        self.worker1 = models.Worker.objects.create(
            last_name='Таня',
            first_name='Морозова',
            middle_name='Никитична',
            gender=consts.FEMALE,
            birth=datetime.date(2003, 3, 31)
        )
        models.WorkerOrganization.objects.create(
            worker=self.worker1,
            mis_id=1,
            org_id=1,
            post='Повар',
            shop='ПФП',
            end_work_date=datetime.date(2020, 3, 31)
        )
        self.worker2 = models.Worker.objects.create(
            last_name='Надя',
            first_name='Попкова',
            middle_name='Ивановна',
            gender=consts.FEMALE,
            birth=datetime.date(2003, 3, 31)
        )
        models.WorkerOrganization.objects.create(
            worker=self.worker2,
            mis_id=2,
            org_id=2,
            post='Повар',
            shop='ПФПА',
        )


    def test_search_last_name(self):
        params = {
            'last_name': 'Таня'
        }

        response = self.client.get(self.get_url(), params)
        result = models.Worker.objects.filter(last_name__istartswith=params['last_name'])

        self.assertEqual(list(result), list(response.context_data['object_list']))

    def test_search_first_name(self):
        params = {
            'first_name': 'Морозова'
        }

        response = self.client.get(self.get_url(), params)
        result = models.Worker.objects.filter(first_name__istartswith=params['first_name'])

        self.assertEqual(list(result), list(response.context_data['object_list']))

    def test_search_middle_name(self):
        params = {
            'middle_name': 'Никитична'
        }

        response = self.client.get(self.get_url(), params)
        result = models.Worker.objects.filter(middle_name__istartswith=params['middle_name'])

        self.assertEqual(list(result), list(response.context_data['object_list']))


    @mock.patch.object(Org, 'get')
    def test_search_org(self, mock_org):
        mock_org.return_value = Org(
            id=1,
            name='Рога',
            legal_name='ООО Рога'
        )
        params = {
            'orgs': [1]
        }

        response = self.client.get(self.get_url(), params)
        result = models.Worker.objects.filter(worker_orgs__org_id__in=params['orgs'])

        self.assertEqual(list(result), list(response.context_data['object_list']))
    
    def test_search_post(self):
        params = {
            'post': 'Повар'
        }

        response = self.client.get(self.get_url(), params)
        result = models.Worker.objects.filter(worker_orgs__post__istartswith=params['post'])

        self.assertEqual(list(result), list(response.context_data['object_list']))

    def test_search_shop(self):
        params = {
            'shop': 'ПФП'
        }

        response = self.client.get(self.get_url(), params)
        result = models.Worker.objects.filter(worker_orgs__shop__istartswith=params['shop'])

        self.assertEqual(list(result), list(response.context_data['object_list']))

    def test_search_work_false(self):
        params = {
            'is_active': '0',
        }

        response = self.client.get(self.get_url(), params)
        result = models.Worker.objects.filter(worker_orgs__end_work_date__isnull=False)

        self.assertEqual(list(result), list(response.context_data['object_list']))

    def test_search_work_true(self):
        params = {
            'is_active': '1',
        }

        response = self.client.get(self.get_url(), params)
        result = models.Worker.objects.filter(worker_orgs__end_work_date__isnull=True)

        self.assertEqual(list(result), list(response.context_data['object_list']))