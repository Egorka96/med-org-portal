import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass
from typing import Dict, List, Tuple

import requests
from django.conf import settings
from django.utils.timezone import now
from djutils.date_utils import iso_to_date

from mis.law_item import LawItem
from mis.org import Org
from mis.service_client import Mis


@dataclass
class Direction:
    number: int
    last_name: str
    first_name: str
    birth: datetime.date
    gender: str
    exam_type: str = None

    from_date: datetime.date = None
    to_date: datetime.date = None

    middle_name: str = None
    org: Org = None
    post: str = None
    shop: str = None
    law_items_section_1: List[LawItem] = None
    law_items_section_2: List[LawItem] = None
    pay_method: dict = None

    def __str__(self):
        fio = ' '.join(filter(bool, [self.last_name, self.first_name, self.middle_name]))

        label = f'Направление "{fio}"'
        if self.from_date:
            label += f' c {self.from_date.strftime("%d.%m.%Y")}'
        if self.to_date:
            label += f' по {self.to_date.strftime("%d.%m.%Y")}'

        return label

    @classmethod
    def filter(cls, params: Dict = None) -> List['Direction']:
        directions = []
        for item in Mis().request(path='/api/pre_record/', params=params)['results']:
            directions.append(cls(
                number=item['id'],
                last_name=item['last_name'],
                first_name=item['first_name'],
                middle_name=item['middle_name'],
                birth=iso_to_date(item['birth']),
                gender=item['gender'],
                from_date=iso_to_date(item['date_from']),
                to_date=iso_to_date(item['date_to']),
                org=Org.get_from_dict(data=item['org']) if item.get('org') else None,
                pay_method=item['pay_method'],
                exam_type=item['exam_type'],
                post=item['post'],
                shop=item['shop'],
                law_items_section_1=[LawItem.get_from_dict(l_i) for l_i in item.get('law_items', []) if l_i['section'] == '1'],
                law_items_section_2=[LawItem.get_from_dict(l_i) for l_i in item.get('law_items', []) if l_i['section'] == '2']
            ))
        return directions

    @classmethod
    def get(cls, direction_id) -> 'Direction':
        result = Mis().request(path=f'/api/pre_record/{direction_id}/')
        direction = cls(
            number=result['id'],
            last_name=result['last_name'],
            first_name=result['first_name'],
            middle_name=result['middle_name'],
            birth=iso_to_date(result['birth']),
            gender=result['gender'],
            from_date=iso_to_date(result['date_from']),
            to_date=iso_to_date(result['date_to']),
            org=Org.get_from_dict(data=result['org']) if result.get('org') else None,
            pay_method=result['pay_method'],
            exam_type=result['exam_type'],
            post=result['post'],
            shop=result['shop'],
            law_items_section_1=[LawItem.get_from_dict(l_i) for l_i in result.get('law_items', []) if l_i['section'] == '1'],
            law_items_section_2=[LawItem.get_from_dict(l_i) for l_i in result.get('law_items', []) if l_i['section'] == '2']
        )
        return direction

    @classmethod
    def create(cls, params) -> Tuple[bool, str]:
        url = settings.MIS_URL + '/api/pre_record/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        params['date_from'] = now().date()
        params['date_to'] = params['date_from'] + relativedelta(days=settings.DIRECTION_ACTION_DAYS)
        params['order_types'] = [2]  # ПРОФ осмотр

        if params.get('law_items_section_1') or params.get('law_items_section_2'):
            params['law_items'] = [*params.get('law_items_section_1', []), *params.get('law_items_section_2', [])]

        response = requests.post(url, data=params, headers=headers)
        response_data = response.json()

        if response.status_code == 201:
            success = True
            description = f'Направление создано: Номер {response_data["id"]}'
        elif response.status_code == 400:
            success = False
            description = f'Ошибка создания направления: {response_data["error"]}'
        elif response.status_code > 499:
            success = False
            description = f'Невозможно создать направление в МИС - ошибка на сервере МИС'
        else:
            raise Exception('Unexpected status code o_O')

        return success, description

    @classmethod
    def edit(cls, direction_id, params) -> Tuple[bool, str]:
        url = settings.MIS_URL + f'/api/pre_record/{direction_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        params['order_types'] = [2]  # ПРОФ осмотр

        if params.get('law_items_section_1') or params.get('law_items_section_2'):
            params['law_items'] = [*params.get('law_items_section_1', []), *params.get('law_items_section_2', [])]

        response = requests.put(url, data=params, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            success = True
            description = f'Направление успешно изменено.'
        elif response.status_code == 400:
            success = False
            description = f'Ошибка редактирования направления: {response_data["error"]}'
        elif response.status_code > 499:
            success = False
            description = f'Невозможно изменить направление в МИС - ошибка на сервере МИС'
        else:
            raise Exception('Unexpected status code o_O')

        return success, description

    @classmethod
    def delete(cls, direction_id) -> Tuple[bool, str]:
        url = settings.MIS_URL + f'/api/pre_record/{direction_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.delete(url, headers=headers)

        if response.status_code == 204:
            success = True
            description = f'Направление успешно удалено.'
        elif 399 < response.status_code < 500:
            success = False
            description = f'Ошибка удаления направления: Ошибка запроса'
        elif response.status_code > 499:
            success = False
            description = f'Невозможно удалить направление в МИС - ошибка на сервере МИС'
        else:
            raise Exception('Unexpected status code o_O')

        return success, description
