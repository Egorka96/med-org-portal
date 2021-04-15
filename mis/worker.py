import datetime
from dataclasses import dataclass
from typing import Dict, List, Tuple

from djutils.date_utils import iso_to_date
from django.conf import settings
import requests

from mis.document import Document
from mis.law_item import LawItem
from mis.org import Org
from mis.service_client import Mis


@dataclass
class Worker:
    id: int
    org: Org
    last_name: str
    first_name: str
    birth: datetime.date
    gender: str

    middle_name: str = None
    post: str = None
    shop: str = None
    law_items: List[LawItem] = None

    documents: List[Document] = None

    def __str__(self):
        return ' '.join(filter(bool, [self.last_name, self.first_name, self.middle_name]))

    @classmethod
    def filter(cls, params: Dict = None, user=None) -> List['Worker']:
        workers = []
        for item in Mis().request(path='/api/workers/', params=params, user=user)['results']:
            workers.append(cls.get_from_dict(item))
        return workers

    @classmethod
    def get(cls, worker_id, user=None) -> 'Worker':
        result = Mis().request(path=f'/api/workers/{worker_id}/')
        worker = cls.get_from_dict(result, user)
        return worker

    @classmethod
    def get_from_dict(cls, data: dict, user=None) -> 'Worker':
        if data.get('visits'):
            available_document_type_ids = user.core.available_document_type_ids.values_list('document_type_id', flat=True)\
                                            if user else []

            data['documents'] = []
            for date_data in data['visits']:
                for document_data in date_data.get('documents', []):
                    if document_data['doc_type']['id'] not in available_document_type_ids:
                        continue
                    document_data['date'] = iso_to_date(date_data['date'])
                    data['documents'].append(Document.get_from_dict(document_data))

        return cls(
            id=data['id'],
            last_name=data['last_name'],
            first_name=data['first_name'],
            middle_name=data['middle_name'],
            birth=iso_to_date(data['birth']),
            gender=data['gender'],
            org=Org.get_from_dict(data=data['org']) if data.get('org') else None,
            post=data['post'],
            shop=data['shop'],
            law_items=[LawItem.get_from_dict(l_i) for l_i in data.get('law_items', [])],
            documents=data.get('documents')
        )

    @classmethod
    def create(cls, params) -> Tuple[bool, str, dict]:
        url = settings.MIS_URL + '/api/workers/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        params['law_items'] = []
        for field_name in ('law_items_302_section_1', 'law_items_302_section_2', 'law_items_29'):
            params['law_items'].extend(params.get(field_name, []))

        params['birth'] = params['birth'].isoformat()
        if params['start_work_date']:
            params['start_work_date'] = params['start_work_date'].isoformat()

        if params['end_work_date']:
            params['end_work_date'] = params['end_work_date'].isoformat()

        response = requests.post(url, json=params, headers=headers)
        response_data = response.json()

        if response.status_code == 201:
            success = True
            description = f'Сотрудник создан: Номер {response_data["id"]}'
        elif response.status_code == 400:
            success = False
            description = f'Ошибка создания сотрудника: {response_data["error"]}'
        elif response.status_code > 499:
            success = False
            description = f'Невозможно создать сотрудника в МИС - ошибка на сервере МИС'
        else:
            raise Exception('Unexpected status code o_O')

        return success, description, response_data

    @classmethod
    def edit(cls, worker_id, params) -> Tuple[bool, str, dict]:
        url = settings.MIS_URL + f'/api/workers/{worker_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        params['law_items'] = []
        for field_name in ('law_items_302_section_1', 'law_items_302_section_2', 'law_items_29'):
            params['law_items'].extend(params.get(field_name, []))

        params['birth'] = params['birth'].isoformat()
        if params['start_work_date']:
            params['start_work_date'] = params['start_work_date'].isoformat()

        if params['end_work_date']:
            params['end_work_date'] = params['end_work_date'].isoformat()

        response = requests.put(url, json=params, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            success = True
            description = f'Сотрудник успешно изменен.'
        elif response.status_code == 400:
            success = False
            description = f'Ошибка редактирования сотрудника: {response_data.get("error", response_data)}'
        elif response.status_code > 499:
            success = False
            description = f'Невозможно изменить направление в МИС - ошибка на сервере МИС'
        else:
            raise Exception('Unexpected status code o_O')

        return success, description, response_data

    @classmethod
    def delete(cls, worker_id) -> Tuple[bool, str]:
        url = settings.MIS_URL + f'/api/workers/{worker_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.delete(url=url, headers=headers)

        if response.status_code == 204:
            success = True
            description = f'Сотрудник успешно удален.'
        elif 399 < response.status_code < 500:
            response_data = response.json()
            if response_data.get('error'):
                response_data = response_data['error']
            elif response_data.get('detail'):
                response_data = response_data['detail']
            success = False
            description = f'Ошибка удаления сотрудника: ' + response_data
        elif response.status_code > 499:
            success = False
            description = f'Невозможно удалить сотрудника в МИС - ошибка на сервере МИС'
        else:
            raise Exception('Unexpected status code o_O')

        return success, description

