import datetime
from unittest import mock

from coverage.backunittest import TestCase
from django.test import override_settings
from kombu.utils import json
from mis.document import DocumentType, Document
from requests import Response
from project import settings


class DocumentTypeTests(TestCase):
    MIS_URL = 'http://127.0.0.1:8000'

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.get')
    @override_settings(MIS_URL=MIS_URL)
    def test_filter(self, mock_request):
        response_json = [{
                'id': 1,
                'name': 'Обходной лист'
            },
            {
                'id': 2,
                'name': 'Простой лист'
            },
            {
                'id': 3,
                'name': 'Обычный лист'
        }]
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        document_types = []
        for item in response_json:
            document_types.append(DocumentType(
                id=item['id'],
                name=item['name']
            ))
        params_filter = {'name': 'ХАХАХА'}
        expect_params = {
            'url': self.MIS_URL + f'/api/document_type/',
            'params': params_filter,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }

        document_type = DocumentType.filter(params_filter)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)
        self.assertEqual(document_types, document_type)

    @mock.patch('requests.get')
    @override_settings(MIS_URL=MIS_URL)
    def test_get(self, mock_request):
        doc_id = 1
        response_json = {
            'id': 1,
            'name': 'Обходной лист'
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        expect_params = {
            'url': self.MIS_URL + f'/api/document_type/{doc_id}/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }
        expect_document_type = DocumentType(
            id=response_json['id'],
            name=response_json['name']
        )

        document_type = DocumentType.get(doc_id)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)
        self.assertEqual(expect_document_type, document_type)


class DocumentTests(TestCase):
    MIS_URL = 'http://127.0.0.1:8000'

    def get_response(self, content: bytes, status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = content
        return response

    @mock.patch('requests.get')
    @override_settings(MIS_URL=MIS_URL)
    def test_get_content(self, mock_request):
        path = '/path/to/file/'
        with open('%s/core/tests/test_mis/test.txt' % settings.BASE_DIR, mode='rb') as file:
            mock_request.return_value = self.get_response(content=file.read())

        expect_params = {
            'url': self.MIS_URL + path,
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'}
        }

        Document.get_content(path)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    def test_get_from_dict(self):
        document_type_data = {
            'id': 1,
            'name': 'doc_type'
        }
        document_data = {
            'date': datetime.date(2021, 2, 15),
            'doc_type': document_type_data,
            'doc_link': '/path/to/'
        }

        document_type = DocumentType(
            id=document_type_data['id'],
            name=document_type_data['name']
        )
        document = Document(
            date=document_data['date'],
            document_type= document_type,
            document_link=document_data['doc_link']
        )

        self.assertEqual(document, Document.get_from_dict(document_data))
