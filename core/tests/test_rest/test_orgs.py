import dataclasses
import json
from unittest import mock

from django.http import QueryDict
from django.urls import reverse
from rest_framework.test import APITestCase

from core.datatools.string import random_word
from core.tests.base import BaseRestTestCase
from core import models
from mis.org import Org


class TestOrgs(BaseRestTestCase, APITestCase):

    def generate_data(self):
        super().generate_data()
        self.core_user = models.User.objects.create(django_user=self.user)
        self.url = reverse('core:rest_orgs')

    def get_mocked_orgs(self):
        orgs = []
        for i in range(3):
            org = Org(
                id=i,
                name=random_word(10),
                legal_name=random_word(10),
            )
            orgs.append(dataclasses.asdict(org))

        return {
            'count': len(orgs),
            'previous': None,
            'next': None,
            'results': orgs
        }

    @mock.patch.object(Org, 'filter_raw')
    def test_orgs(self, mock_orgs):
        mock_orgs.return_value = self.get_mocked_orgs()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], mock_orgs.return_value['count'])
        self.assertEqual(response.data['results'], mock_orgs.return_value['results'])
        self.assertEqual(response.data['previous'], mock_orgs.return_value['previous'])
        self.assertEqual(response.data['next'], mock_orgs.return_value['next'])

        expect_params = {'params': QueryDict()}
        self.assertEqual(expect_params, mock_orgs.call_args_list[0].kwargs)

    @mock.patch.object(Org, 'filter_raw')
    def test_orgs_filter(self, mock_orgs):
        mock_orgs.return_value = self.get_mocked_orgs()

        filter_params = {'name': ['test']}
        response = self.client.get(self.url, data=filter_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], mock_orgs.return_value['count'])
        self.assertEqual(response.data['results'], mock_orgs.return_value['results'])
        self.assertEqual(response.data['previous'], mock_orgs.return_value['previous'])
        self.assertEqual(response.data['next'], mock_orgs.return_value['next'])

        mock_orgs.call_args_list[0].kwargs['params'] = dict(mock_orgs.call_args_list[0].kwargs['params'])
        self.assertEqual(filter_params, mock_orgs.call_args_list[0].kwargs['params'])

    @mock.patch.object(Org, 'filter_raw')
    def test_orgs_with_user_constraint(self, mock_orgs):
        mock_orgs.return_value = self.get_mocked_orgs()
        self.core_user.org_ids = json.dumps([1, 5])
        self.core_user.save()

        filter_params = {'name': ['test']}
        response = self.client.get(self.url, data=filter_params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], mock_orgs.return_value['count'])
        self.assertEqual(response.data['results'], mock_orgs.return_value['results'])
        self.assertEqual(response.data['previous'], mock_orgs.return_value['previous'])
        self.assertEqual(response.data['next'], mock_orgs.return_value['next'])

        mock_orgs.call_args_list[0].kwargs['params'] = dict(mock_orgs.call_args_list[0].kwargs['params'])
        expect_params = filter_params
        expect_params['id'] = [json.loads(self.core_user.org_ids)]
        self.assertEqual(expect_params, mock_orgs.call_args_list[0].kwargs['params'])
