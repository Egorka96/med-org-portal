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
    confirm_date: datetime.date = None

    def __str__(self):
        fio = ' '.join(filter(bool, [self.last_name, self.first_name, self.middle_name]))

        label = f'Направление "{fio}"'
        if self.from_date:
            label += f' c {self.from_date.strftime("%d.%m.%Y")}'
        if self.to_date:
            label += f' по {self.to_date.strftime("%d.%m.%Y")}'

        return label

    @classmethod
    def dict_to_obj(cls, data: dict) -> 'Direction':
        return cls(
            number=data['id'],
            last_name=data['last_name'],
            first_name=data['first_name'],
            middle_name=data['middle_name'],
            birth=iso_to_date(data['birth']),
            gender=data['gender'],
            from_date=iso_to_date(data['date_from']),
            to_date=iso_to_date(data['date_to']),
            org=Org.get_from_dict(data=data['org']) if data.get('org') else None,
            pay_method=data['pay_method'],
            exam_type=data['exam_type'],
            post=data['post'],
            shop=data['shop'],
            law_items_section_1=[LawItem.get_from_dict(l_i) for l_i in data.get('law_items', []) if
                                 l_i['section'] == '1'],
            law_items_section_2=[LawItem.get_from_dict(l_i) for l_i in data.get('law_items', []) if
                                 l_i['section'] == '2'],
            confirm_date=iso_to_date(data['confirm_dt']),
        )

    @classmethod
    def filter(cls, params: Dict = None) -> List['Direction']:
        directions = []
        for item in Mis().request(path='/api/pre_record/', params=params)['results']:
            directions.append(cls.dict_to_obj(item))
        return directions

    @classmethod
    def get(cls, direction_id) -> 'Direction':
        result = Mis().request(path=f'/api/pre_record/{direction_id}/')
        direction = cls.dict_to_obj(result)
        return direction

    @classmethod
    def create(cls, params) -> Tuple[bool, str]:
        url = settings.MIS_URL + '/api/pre_record/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        params['date_from'] = now().date()
        if getattr(settings, 'DIRECTION_ACTION_DAYS', None):
            params['date_to'] = params['date_from'] + relativedelta(days=settings.DIRECTION_ACTION_DAYS)
        else:
            params['date_to'] = datetime.date(params['date_from'].year, 12, 31)
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
