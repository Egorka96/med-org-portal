import dataclasses
import datetime
from unittest import mock

from core.datatools.string import random_word
from core.tests.base import BaseRestTestCase
from django.urls import reverse
from mis.org import Org
from mis.worker import Worker
from rest_framework.test import APITestCase
from swutils.date import date_to_rus


class TestWorkers(BaseRestTestCase, APITestCase):

    def generate_data(self):
        super().generate_data()
        self.url = reverse('core:rest_workers')

    def get_mocked_workers(self):
        workers = []
        for i in range(3):
            org = Org(
                id=i,
                name=random_word(10)
            )
            worker = Worker(
                id=i,
                org=org,
                last_name=random_word(10),
                first_name=random_word(10),
                birth=datetime.date(2001, 11, 6),
                gender=random_word(10)
            )
            workers.append(worker)
        return workers

    @mock.patch.object(Worker, 'filter')
    def test_workers(self, mock_worker):
        mock_worker.return_value = self.get_mocked_workers()

        response = self.client.get(self.url)
        mock_worker.return_value = [dataclasses.asdict(w) for w in mock_worker.return_value]
        for w in mock_worker.return_value:
            w['birth_rus'] = date_to_rus(w['birth'])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], mock_worker.return_value)

        expect_params = {}

        mock_worker.call_args_list[0].kwargs['params'] = dict(mock_worker.call_args_list[0].kwargs['params'])
        self.assertEqual(expect_params, mock_worker.call_args_list[0].kwargs['params'])

    @mock.patch.object(Worker, 'filter')
    def test_workers_filter(self, mock_worker):
        mock_worker.return_value = self.get_mocked_workers()

        filter_params = {'term': 'test'}
        response = self.client.get(self.url, filter_params)
        mock_worker.return_value = [dataclasses.asdict(w) for w in mock_worker.return_value]
        for w in mock_worker.return_value:
            w['birth_rus'] = date_to_rus(w['birth'])

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], mock_worker.return_value)

        expect_params = {'term': [filter_params['term']]}

        mock_worker.call_args_list[0].kwargs['params'] = dict(mock_worker.call_args_list[0].kwargs['params'])
        self.assertEqual(expect_params, mock_worker.call_args_list[0].kwargs['params'])