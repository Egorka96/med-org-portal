import datetime
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import requests
from django.conf import settings
from django.utils.timezone import now
from djutils.date_utils import iso_to_date
from mis.insurance_policy import InsurancePolicy

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
    law_items: List[LawItem] = None
    pay_method: dict = None
    confirm_date: datetime.date = None
    insurance_policy: InsurancePolicy = None

    def __str__(self):
        fio = self.get_fio()
        label = f'Направление "{fio}"'
        if self.from_date:
            label += f' c {self.from_date.strftime("%d.%m.%Y")}'
        if self.to_date:
            label += f' по {self.to_date.strftime("%d.%m.%Y")}'

        return label

    def get_fio(self):
        return ' '.join(filter(bool, [self.last_name, self.first_name, self.middle_name]))

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
            law_items=[LawItem.get_from_dict(l_i) for l_i in data.get('law_items', [])],
            confirm_date=iso_to_date(data['confirm_dt']),
            insurance_policy=InsurancePolicy.get_from_dict(data=data['insurance_policy'])
                             if data.get('insurance_policy') else None
        )

    @classmethod
    def filter_raw(cls, params: Dict = None, user: 'core.models.DjangoUser' = None):
        response_json = Mis().request(path='/api/pre_record/', params=params, user=user)

        directions = []
        for item in response_json['results']:
            directions.append(asdict(cls.dict_to_obj(item)))

        response_json['results'] = directions
        return response_json

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
    def create(cls, params) -> Tuple[int, str]:
        url = settings.MIS_URL + '/api/pre_record/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        params['date_from'] = now().date()
        if getattr(settings, 'DIRECTION_ACTION_DAYS', None):
            params['date_to'] = params['date_from'] + relativedelta(days=settings.DIRECTION_ACTION_DAYS)
        else:
            params['date_to'] = datetime.date(params['date_from'].year, 12, 31)
        params['order_types'] = [2]  # ПРОФ осмотр

        params['law_items'] = []
        for field_name in ('law_items_302_section_1', 'law_items_302_section_2', 'law_items_29'):
            params['law_items'].extend(params.get(field_name, []))

        if params.get('insurance_number'):
            params['insurance_policy'] = {
                'number': params['insurance_number']
            }

        params['birth'] = params['birth'].isoformat()
        params['date_to'] = params['date_to'].isoformat()
        params['date_from']= params['date_from'].isoformat()
        params = {key: value for key, value in params.items() if value}

        response = requests.post(url, json=params, headers=headers)
        response_data = response.json()

        if response.status_code == 201:
            description_id = response_data["id"]
            description = f'Направление создано: Номер {response_data["id"]}'
        elif response.status_code == 400:
            description_id = None
            description = f'Ошибка создания направления: {response_data["error"]}'
        elif response.status_code > 499:
            description_id = None
            description = f'Невозможно создать направление в МИС - ошибка на сервере МИС'
        else:
            raise Exception('Unexpected status code o_O')

        return description_id, description

    @classmethod
    def edit(cls, direction_id, params) -> Tuple[int, str]:
        url = settings.MIS_URL + f'/api/pre_record/{direction_id}/'
        headers = {
            'Authorization': f'Token {settings.MIS_TOKEN}',
        }
        params['order_types'] = [2]  # ПРОФ осмотр

        params['law_items'] = []
        for field_name in ('law_items_302_section_1', 'law_items_302_section_2', 'law_items_29'):
            params['law_items'].extend(params.get(field_name, []))

        if params.get('insurance_number'):
            params['insurance_policy'] = {
                'number': params['insurance_number']
            }

        params['birth'] = params['birth'].isoformat()
        params = {key: value for key, value in params.items() if value}

        response = requests.put(url=url, json=params, headers=headers, )
        response_data = response.json()

        if response.status_code == 200:
            description_id = response_data["id"]
            description = f'Направление успешно изменено.'
        elif response.status_code == 400:
            description_id = None
            description = f'Ошибка редактирования направления: {response_data.get("error", response_data)}'
        elif response.status_code > 499:
            description_id = None
            description = f'Невозможно изменить направление в МИС - ошибка на сервере МИС'
        else:
            raise Exception('Unexpected status code o_O')

        return description_id, description

    @classmethod
    def delete(cls, direction_id) -> Tuple[bool, str]:
        url = settings.MIS_URL + f'/api/pre_record/{direction_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.delete(url=url, headers=headers)

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

    def get_law_items(self, law_name: str = None, section: int = None) -> List[LawItem]:
        law_items = self.law_items

        if law_name:
            law_items = list(filter(lambda l_i: l_i.law.name == law_name, law_items))
        if section:
            law_items = list(filter(lambda l_i: l_i.section == section, law_items))

        return law_items
