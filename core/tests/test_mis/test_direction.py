from unittest import TestCase
import datetime
from unittest import mock

from django.test import override_settings
from kombu.utils import json
from requests import Response
from mis.direction import Direction
from django.conf import settings


class DirectionTests(TestCase):
    MIS_URL = 'http://127.0.0.1:8000'

    def get_response(self, content='', status_code=200):
        response = Response()
        response.status_code = status_code
        response._content = bytes(content, encoding='utf-8')
        return response

    def get_direction_params(self):
        return {
            'id': 1,
            'last_name': 'Сидоров',
            'first_name': 'Василий',
            'birth': datetime.date(2002, 5, 12).isoformat(),
            'gender': 'Мужчина',
            'exam_type': '',
            'date_from': None,
            'middle_name': '',
            'post': '',
            'shop': '',
            'pay_method': '',
            'confirm_dt': '',
            'date_to': None
        }

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_filter(self, mock_request):
        response_json = {
            'results':[{
                'id': 1,
                'last_name': 'Сидоров',
                'first_name': 'Василий',
                'birth': datetime.date(2002, 5, 12).isoformat(),
                'gender': 'Мужчина',
                'exam_type': '',
                'date_from': None,
                'middle_name': '',
                'post': '',
                'shop': '',
                'pay_method': '',
                'confirm_dt': '',
                'date_to': None
            },
            {
                'id': 2,
                'last_name': 'Яковлев',
                'first_name': 'Иван',
                'birth': datetime.date(1976, 11, 6).isoformat(),
                'gender': 'Мужчина',
                'exam_type': '',
                'date_from': None,
                'middle_name': '',
                'post': '',
                'shop': '',
                'pay_method': '',
                'confirm_dt': '',
                'date_to': None
            }]
        }
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        params = {'last_name': 'Сидоров'}

        directions_expected = []
        for item in response_json['results']:
            directions_expected.append(Direction(
                number=item['id'],
                last_name=item['last_name'],
                first_name=item['first_name'],
                birth=datetime.datetime.strptime(item['birth'], "%Y-%m-%d").date(),
                gender=item['gender'],
                exam_type=item['exam_type'],
                from_date=item['date_from'],
                middle_name=item['middle_name'],
                post=item['post'],
                shop=item['shop'],
                pay_method=item['pay_method'],
                law_items_section_1=[],
                law_items_section_2=[]
            ))

        directions = Direction.filter(params)
        self.assertEqual(directions_expected, directions)

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_get(self, mock_request):
        response_json = self.get_direction_params()
        mock_request.return_value = self.get_response(content=json.dumps(response_json))

        direction_id = 1
        expect_params = {
            'url': self.MIS_URL + f'/api/pre_record/{direction_id}/',
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'params': None,
            'method': 'get',
            'data': None
        }

        Direction.get(direction_id=direction_id)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.post')
    @override_settings(MIS_URL=MIS_URL)
    def test_create(self, mock_request):
        response_json = self.get_direction_params()
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=201)

        params = {
            'number': response_json['id'],
            'last_name': response_json['last_name'],
            'first_name': response_json['first_name'],
            'birth': response_json['birth'],
            'gender': response_json['gender'],
            'exam_type': response_json['exam_type'],
            'date_from': response_json['date_from'],
            'middle_name': response_json['middle_name'],
            'post': response_json['post'],
            'shop': response_json['shop'],
            'pay_method': response_json['pay_method'],
            'law_items_section_1': [],
            'law_items_section_2': []
        }
        expect_params = {
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'data': params,
        }
        expect_result = (True, f'Направление создано: Номер {response_json["id"]}')

        direction_result = Direction.create(params)
        self.assertEqual(direction_result, expect_result)
        self.assertEqual(expect_params, mock_request.call_args_list[0].kwargs)

    @mock.patch('requests.post')
    @override_settings(MIS_URL=MIS_URL)
    def test_create_status_code_400(self, mock_request):
        response_json = {'error': "Бах, все сломалось"}
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=400)

        params = self.get_direction_params()

        expect_result = (False, f'Ошибка создания направления: {response_json["error"]}')

        direction_result = Direction.create(params)
        self.assertEqual(direction_result, expect_result)

    @mock.patch('requests.post')
    @override_settings(MIS_URL=MIS_URL)
    def test_create_status_code_500(self, mock_request):
        response_json = 'Невозможно создать направление в МИС - ошибка на сервере МИС'
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=500)

        params = self.get_direction_params()

        expect_result = (False, 'Невозможно создать направление в МИС - ошибка на сервере МИС')

        direction_result = Direction.create(params)
        self.assertEqual(direction_result, expect_result)

    @mock.patch('requests.put')
    @override_settings(MIS_URL=MIS_URL)
    def test_edit(self, mock_request):
        response_json = self.get_direction_params()
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=200)

        params = self.get_direction_params()
        params['last_name'] = 'Яковлев'
        direction_id = params['id']
        expect_result = (True, f'Направление успешно изменено.')
        expect_params = {
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'data': params,
        }

        direction_result = Direction.edit(direction_id, params)
        self.assertEqual(direction_result, expect_result)
        self.assertEqual(mock_request.call_args_list[0].kwargs, expect_params)

    @mock.patch('requests.put')
    @override_settings(MIS_URL=MIS_URL)
    def test_edit_status_code_400(self, mock_request):
        response_json = {'error': "Бах, все сломалось"}
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=400)

        params = self.get_direction_params()
        params['last_name'] = 'Яковлев'
        direction_id = params['id']
        expect_result = (False, f'Ошибка редактирования направления: {response_json["error"]}')

        direction_result = Direction.edit(direction_id, params)
        self.assertEqual(direction_result, expect_result)

    @mock.patch('requests.put')
    @override_settings(MIS_URL=MIS_URL)
    def test_edit_status_code_500(self, mock_request):
        response_json = f'Невозможно изменить направление в МИС - ошибка на сервере МИС'
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=500)

        params = self.get_direction_params()
        params['last_name'] = 'Яковлев'
        direction_id = params['id']
        expect_result = (False, 'Невозможно изменить направление в МИС - ошибка на сервере МИС')

        direction_result = Direction.edit(direction_id, params)
        self.assertEqual(direction_result, expect_result)

    @mock.patch('requests.delete')
    @override_settings(MIS_URL=MIS_URL)
    def test_delete(self, mock_request):
        response_json = self.get_direction_params()
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=204)
        direction_id = response_json['id']
        expect_result = (True, 'Направление успешно удалено.')
        expect_params = {
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
        }

        direction_result = Direction.delete(direction_id)
        self.assertEqual(direction_result, expect_result)
        self.assertEqual(mock_request.call_args_list[0].kwargs, expect_params)

    @mock.patch('requests.delete')
    @override_settings(MIS_URL=MIS_URL)
    def test_delete_status_code_400(self, mock_request):
        response_json = {'error': "Бах, все сломалось"}
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=400)

        direction_id = 1
        expect_result = (False, 'Ошибка удаления направления: Ошибка запроса')

        direction_result = Direction.delete(direction_id)
        self.assertEqual(direction_result, expect_result)

    @mock.patch('requests.delete')
    @override_settings(MIS_URL=MIS_URL)
    def test_delete_status_code_500(self, mock_request):
        response_json = 'Невозможно удалить направление в МИС - ошибка на сервере МИС'
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=500)

        direction_id = 1
        expect_result = (False, 'Невозможно удалить направление в МИС - ошибка на сервере МИС')

        direction_result = Direction.delete(direction_id)
        self.assertEqual(direction_result, expect_result)



