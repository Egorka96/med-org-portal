from unittest import mock

from coverage.backunittest import TestCase
from django.test import override_settings
from mis.org import Org
from requests import Response
from rest_framework.utils import json
from django.conf import settings



class OrgTests(TestCase):
    MIS_URL = 'http://127.0.0.1:8000'

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.get')
    @override_settings(MIS_URL=MIS_URL)
    def test_filter(self, mock_request):
        response_json = {
            'results':[{
                'id': 1,
                'name': 'Организация 1',
                'legal_name': 'ООО "Организация 1" '
            },
            {
                'id': 2,
                'name':'Организация 2',
                'legal_name': 'ОАО "Организация 2" '
            },
            {
                'id': 3,
                'name': 'Организация 3',
                'legal_name': 'ООО "Организация 3" '
            }]
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        expected_orgs = []
        for item in response_json['results']:
            org = Org(id=item['id'], name=item['name'], legal_name=item['legal_name'])
            expected_orgs.append(org)

        filter_params = {'name': 'Организация 1'}
        expect_params = {
            'url': self.MIS_URL + '/api/orgs/',
            'params': filter_params,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }

        orgs = Org.filter(params=filter_params)
        self.assertEqual(expected_orgs, orgs)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.get')
    @override_settings(MIS_URL=MIS_URL)
    def test_get(self, mock_request):
        get_params = 1
        response_json = {
            'id': get_params,
            'name': 'Организация 1',
            'legal_name': 'ОАО "Организация 1" '
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        org = Org(id=response_json['id'], name=response_json['name'], legal_name=response_json['legal_name'])

        expect_params = {
            'url': self.MIS_URL + f'/api/orgs/{get_params}/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }

        orgs = Org.get(get_params)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)
        self.assertEqual(org, orgs)








