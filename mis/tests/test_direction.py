from copy import copy
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
            'birth': datetime.date(2002, 5, 12),
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

    def get_direction_params_list(self):
        return {
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

    @mock.patch('requests.request')
    @override_settings(MIS_URL=MIS_URL)
    def test_filter(self, mock_request):
        response_json = self.get_direction_params_list()
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
                law_items=[],
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

        params = self.get_direction_params()
        params = {key: value for key, value in params.items() if value}
        expect_json = copy(params)
        expect_json['birth'] = params['birth'].isoformat()
        expect_json['date_from'] = datetime.date.today()
        expect_json['date_to'] = datetime.date(expect_json['date_from'].year, 12, 31).isoformat()
        expect_json['date_from'] = expect_json['date_from'].isoformat()
        expect_json['order_types'] = [2]
        expect_params = {
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'json': expect_json,
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
        expect_result = (None, f'Ошибка создания направления: {response_json["error"]}')

        direction_result = Direction.create(params)
        self.assertEqual(direction_result, expect_result)

    @mock.patch('requests.post')
    @override_settings(MIS_URL=MIS_URL)
    def test_create_status_code_500(self, mock_request):
        response_json = 'Невозможно создать направление в МИС - ошибка на сервере МИС'
        mock_request.return_value = self.get_response(content=json.dumps(response_json), status_code=500)

        params = self.get_direction_params()
        expect_result = (None, 'Невозможно создать направление в МИС - ошибка на сервере МИС')

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
        params = {key: value for key, value in params.items() if value}
        expect_json = copy(params)
        expect_json['birth'] = params['birth'].isoformat()
        expect_json['order_types'] = [2]
        expect_params = {
            'headers': {'Authorization': f'Token {settings.MIS_TOKEN}'},
            'json': expect_json,
            'url': self.MIS_URL + f'/api/pre_record/{direction_id}/'
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
        expect_result = (None, f'Ошибка редактирования направления: {response_json["error"]}')

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
        expect_result = (None, 'Невозможно изменить направление в МИС - ошибка на сервере МИС')

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
            'url': self.MIS_URL + f'/api/pre_record/{direction_id}/'
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



