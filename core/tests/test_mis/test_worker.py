import datetime
from unittest import TestCase
import json
from unittest import mock

from core import models
from django.contrib.auth import get_user_model
from django.test import override_settings
from mis.document import Document, DocumentType
from mis.org import Org
from mis.worker import Worker
from requests import Response
from django.conf import settings
from djutils.date_utils import iso_to_date

User = get_user_model()


class WorkerTests(TestCase):
    MIS_URL = 'http://127.0.0.1:8000'

    def setUp(self):
        self.generate_data()

    def generate_data(self):
        self.user, _ = User.objects.get_or_create(
            username='test',
            password='test',
        )
        self.core_user, _ = models.User.objects.get_or_create(django_user=self.user, org_ids=json.dumps([1, 5]))

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_filter(self, mock_request):
        org_data = {
            'id': 1,
            'name': 'Организация 1',
            'legal_name': 'ООО "Организация 1" '
        }
        org = Org(
            id=org_data['id'],
            name=org_data['name'],
            legal_name=org_data['legal_name']
        )

        response_json = {
            'results':[{
                'id': 1,
                'org': org_data,
                'last_name': 'Иванов',
                'first_name': 'Иван',
                'birth': datetime.date(2001, 11, 6).isoformat(),
                'gender': 'Мужчина',
                'middle_name': 'Иванович',
                'post': 'БПО Сотрудник.',
                'shop': ''
            },
            {
                'id': 2,
                'org': org_data,
                'last_name': 'Сидоров',
                'first_name': 'Василий',
                'birth': datetime.date(2000, 1, 6).isoformat(),
                'gender': 'Мужчина',
                'middle_name': 'Иванович',
                'post': 'БПО Сотрудник.',
                'shop': ''
            }]
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        params = {'last_name': 'Сидоров'}

        workers_expected = []
        for item in response_json['results']:
            workers_expected.append(Worker(
                id=item['id'],
                org=org,
                last_name=item['last_name'],
                first_name=item['first_name'],
                birth=datetime.datetime.strptime(item['birth'], "%Y-%m-%d").date(),
                gender=item['gender'],
                middle_name=item['middle_name'],
                post=item['post'],
                shop=item['shop'],
                law_items_section_1=[],
                law_items_section_2=[],
            ))

        workers = Worker.filter(params)
        self.assertEqual(workers, workers_expected)

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_filter_user(self, mock_request):
        params = {'last_name': 'Сидоров'}
        expect_params = {
            'url': self.MIS_URL + '/api/workers/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'method': 'get',
            'params': {'last_name': 'Сидоров', 'orgs': json.loads(self.user.core.org_ids)},
            'data': None
        }
        Worker.filter(params, self.user)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_get(self, mock_request):
        worker_id = 1
        org_data = {
            'id': 1,
            'name': 'Организация 1',
            'legal_name': 'ООО "Организация 1" '
        }
        response_json = {
            'id': 1,
            'org': org_data,
            'last_name': 'Иванов',
            'first_name': 'Иван',
            'birth': datetime.date(2001, 11, 6).isoformat(),
            'gender': 'Мужчина',
            'middle_name': 'Иванович',
            'post': 'БПО Сотрудник.',
            'shop': ''
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        expect_params = {
            'url': self.MIS_URL + f'/api/workers/{worker_id}/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'params': None,
            'method': 'get',
            'data': None
        }
        Worker.get(worker_id=worker_id)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_get_from_dict(self, mock_request):
        org_data = {
            'id': 1,
            'name': 'Организация 1',
            'legal_name': 'ООО "Организация 1" '
        }
        org = Org(
            id=org_data['id'],
            name=org_data['name'],
            legal_name=org_data['legal_name']
        )
        response_json = {
            'id': 1,
            'org': org_data,
            'last_name': 'Иванов',
            'first_name': 'Иван',
            'birth': datetime.date(2001, 11, 6).isoformat(),
            'gender': 'Мужчина',
            'middle_name': 'Иванович',
            'post': 'БПО Сотрудник.',
            'shop': '',
            'visits': [{
                'data': "2010-07-08",
                'doc_type': {
                    'id': 4,
                    'name': "Обходной лист"
                },
                'doc_link': "/api/doc/"
            },
            {
                'data': "2001-11-06",
                'doc_type': {
                    'id': 2,
                    'name': "Бланк Согласие"
                },
                'doc_link': "/api/doc/"
            }]
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        worker_expected = Worker(
            id=response_json['id'],
            org=org,
            last_name=response_json['last_name'],
            first_name=response_json['first_name'],
            birth=datetime.datetime.strptime(response_json['birth'], "%Y-%m-%d").date(),
            gender=response_json['gender'],
            middle_name=response_json['middle_name'],
            post=response_json['post'],
            shop=response_json['shop'],
            law_items_section_1=[],
            law_items_section_2=[],
            documents=[]
        )

        worker = Worker.get_from_dict(response_json)
        self.assertEqual(worker_expected, worker)

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_get_from_dict_user(self, mock_request):
        for i in [2, 5, 4]:
             models.UserAvailableDocumentType.objects.create(user=self.core_user, document_type_id=i)

        org_data = {
            'id': 1,
            'name': 'Организация 1',
            'legal_name': 'ООО "Организация 1" '
        }
        org = Org(
            id=org_data['id'],
            name=org_data['name'],
            legal_name=org_data['legal_name']
        )
        response_json = {
            'id': 1,
            'org': org_data,
            'last_name': 'Иванов',
            'first_name': 'Иван',
            'birth': datetime.date(2001, 11, 6).isoformat(),
            'gender': 'Мужчина',
            'middle_name': 'Иванович',
            'post': 'БПО Сотрудник.',
            'shop': '',
            'visits': [{
                'date': "2010-07-08",
                'documents': [{
                    'doc_type': {
                        'id': 4,
                        'name': "Обходной лист"
                    },
                'doc_link': "/api/doc/"
                }]
            },
            {
                'date': "2001-11-06",
                'documents':[{
                    'doc_type': {
                        'id': 2,
                        'name': "Согласие лист"
                    },
                    'doc_link': "/api/doc/"
                }],
            }]
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        worker_expected = Worker(
            id=response_json['id'],
            org=org,
            last_name=response_json['last_name'],
            first_name=response_json['first_name'],
            birth=datetime.datetime.strptime(response_json['birth'], "%Y-%m-%d").date(),
            gender=response_json['gender'],
            middle_name=response_json['middle_name'],
            post=response_json['post'],
            shop=response_json['shop'],
            law_items_section_1=[],
            law_items_section_2=[],
            documents=[]
        )
        document1 = Document(
            date=datetime.datetime.strptime(response_json['visits'][0]['date'], "%Y-%m-%d").date(),
            document_type=DocumentType(**response_json['visits'][0]['documents'][0]['doc_type']),
            document_link=response_json['visits'][0]['documents'][0]['doc_link']
        )

        document2 = Document(
            date=datetime.datetime.strptime(response_json['visits'][1]['date'], "%Y-%m-%d").date(),
            document_type=DocumentType(**response_json['visits'][1]['documents'][0]['doc_type']),
            document_link=response_json['visits'][1]['documents'][0]['doc_link']
        )
        worker_expected.documents = [document1, document2]

        worker = Worker.get_from_dict(response_json, self.user)
        self.assertEqual(worker_expected, worker)

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_get_from_dict_user_one_doc_type(self, mock_request):
        models.UserAvailableDocumentType.objects.all().delete()
        models.UserAvailableDocumentType.objects.create(user=self.core_user, document_type_id=4)
        org_data = {
            'id': 1,
            'name': 'Организация 1',
            'legal_name': 'ООО "Организация 1" '
        }
        org = Org(
            id=org_data['id'],
            name=org_data['name'],
            legal_name=org_data['legal_name']
        )
        response_json = {
            'id': 1,
            'org': org_data,
            'last_name': 'Иванов',
            'first_name': 'Иван',
            'birth': datetime.date(2001, 11, 6).isoformat(),
            'gender': 'Мужчина',
            'middle_name': 'Иванович',
            'post': 'БПО Сотрудник.',
            'shop': '',
            'visits': [{
                'date': "2010-07-08",
                'documents': [{
                    'doc_type': {
                        'id': 4,
                        'name': "Обходной лист"
                    },
                'doc_link': "/api/doc/"
                }]
            },
            {
                'date': "2001-11-06",
                'documents':[{
                    'doc_type': {
                        'id': 2,
                        'name': "Согласие лист"
                    },
                    'doc_link': "/api/doc/"
                }],
            }]
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        worker_expected = Worker(
            id=response_json['id'],
            org=org,
            last_name=response_json['last_name'],
            first_name=response_json['first_name'],
            birth=datetime.datetime.strptime(response_json['birth'], "%Y-%m-%d").date(),
            gender=response_json['gender'],
            middle_name=response_json['middle_name'],
            post=response_json['post'],
            shop=response_json['shop'],
            law_items_section_1=[],
            law_items_section_2=[],
            documents=[]
        )

        document = Document(
            date=datetime.datetime.strptime(response_json['visits'][0]['date'], "%Y-%m-%d").date(),
            document_type=DocumentType(**response_json['visits'][0]['documents'][0]['doc_type']),
            document_link=response_json['visits'][0]['documents'][0]['doc_link']
        )
        worker_expected.documents = [document]

        worker = Worker.get_from_dict(response_json, self.user)
        self.assertEqual(worker_expected, worker)

