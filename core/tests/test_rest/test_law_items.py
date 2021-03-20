import dataclasses
from unittest import mock

from core.datatools.string import random_word
from django.http import QueryDict
from django.urls import reverse
from mis.law_item import LawItem, Law
from rest_framework.test import APITestCase
from core.tests.base import BaseRestTestCase


class TestLawItems(BaseRestTestCase, APITestCase):

    def generate_data(self):
        super().generate_data()
        self.url = reverse('core:rest_law_items')

    def get_mocked_law_items(self):
        law_items = []
        for i in range(3):
            law = Law(
                id=i,
                name=random_word(10)
            )
            law_item = LawItem(
                id=i,
                name=random_word(10),
                section=random_word(10),
                law=law,
                description=random_word(10)
            )
            law_items.append(dataclasses.asdict(law_item))

        return {
            'count': len(law_items),
            'previous': None,
            'next': None,
            'results': law_items
        }

    @mock.patch.object(LawItem, 'filter_raw')
    def test_law_items(self, mock_law_item):
        mock_law_item.return_value = self.get_mocked_law_items()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], mock_law_item.return_value['count'])
        self.assertEqual(response.data['previous'], mock_law_item.return_value['previous'])
        self.assertEqual(response.data['next'], mock_law_item.return_value['next'])
        self.assertEqual(response.data['results'], mock_law_item.return_value['results'])

        expect_params = {'name': [[]] }

        mock_law_item.call_args_list[0].kwargs['params'] = dict(mock_law_item.call_args_list[0].kwargs['params'])
        self.assertEqual(expect_params, mock_law_item.call_args_list[0].kwargs['params'])

    @mock.patch.object(LawItem, 'filter_raw')
    def test_law_items_filter(self, mock_law_item):
        mock_law_item.return_value = self.get_mocked_law_items()

        filter_params = {'term': 'test'}
        response = self.client.get(self.url, data=filter_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], mock_law_item.return_value['count'])
        self.assertEqual(response.data['previous'], mock_law_item.return_value['previous'])
        self.assertEqual(response.data['next'], mock_law_item.return_value['next'])
        self.assertEqual(response.data['results'], mock_law_item.return_value['results'])

        expect_params = {
            'term': [filter_params['term']],
            'name': [[filter_params['term']]]
        }

        mock_law_item.call_args_list[0].kwargs['params'] = dict(mock_law_item.call_args_list[0].kwargs['params'])
        self.assertEqual(expect_params, mock_law_item.call_args_list[0].kwargs['params'])