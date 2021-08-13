from unittest import mock

from coverage.backunittest import TestCase
from django.test import override_settings
from kombu.utils import json
from mis.law_item import LawItem, Law
from requests import Response
from django.conf import settings


class LawItemTests(TestCase):
    MIS_URL = 'http://127.0.0.1:8000'

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_filter(self, mock_request):
        response_json = {
            'results':[{
                'id': 1,
                'name': 'test 1',
                'section': 'test 1',
                'description': 'test 1',
                'display': 'test 1 test 1',
                'law': {
                    'id': 1,
                    'name': '302н'
                }
            },
            {
                'id': 2,
                'name': 'test 2',
                'section': 'test 2',
                'description': 'test 2',
                'display': 'test 2',
                'law': {
                    'id': 2,
                    'name': '29н'
                }
            },
            {
                'id': 3,
                'name': 'test 3',
                'section': 'test 3',
                'description': 'test 3',
                'display': 'test3 test3',
                'law': {
                    'id': 1,
                    'name': '302н'
                }
            }]
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        law_items = []
        for item in response_json['results']:
            law_items.append(LawItem(
                id=item['id'],
                name=item['name'],
                section=item['section'],
                law=Law(id=item['law']['id'], name=item['law']['name']),
                description=item['description'],
                display=item['display']
            ))

        filter_params = {'name': 'test 3'}
        law_item = LawItem.filter(filter_params)
        self.assertEqual(law_items, law_item)

        expect_params = {
            'url': self.MIS_URL + f'/api/law_items/',
            'params': filter_params,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'method': 'get',
            'data': None
        }

        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_get(self, mock_request):
        law_item_id = 1
        response_json = {
            'id': 1,
            'name': 'test 3',
            'section': 'test 3',
            'display': 'test 3 test 3',
            'description': 'test 3',
                'law': {
                    'id': 1,
                    'name': '302н'
                }
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        law_item = LawItem(
            id=response_json['id'],
            name=response_json['name'],
            section=response_json['section'],
            law=Law(id=response_json['law']['id'], name=response_json['law']['name']),
            description=response_json['description'],
            display=response_json['display']
        )

        law_items = LawItem.get(law_item_id)
        self.assertEqual(law_item, law_items)

        expect_params = {
            'url': self.MIS_URL + f'/api/law_items/{law_item_id}/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'method': 'get',
            'data': None,
            'params': None
        }

        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)
