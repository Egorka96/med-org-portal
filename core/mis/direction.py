import datetime
from dataclasses import dataclass
from typing import Dict, List

import requests
from django.conf import settings
from djutils.date_utils import iso_to_date

from core.mis.org import Org


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
    law_items: List[Dict] = None
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
        url = settings.MIS_URL + f'/api/pre_record/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        directions = []
        for item in response.json()['results']:
            directions.append(cls(
                number=item['id'],
                last_name=item['last_name'],
                first_name=item['first_name'],
                middle_name=item['middle_name'],
                birth=iso_to_date(item['birth']),
                gender=item['gender'],
                from_date=iso_to_date(item['date_from']),
                to_date=iso_to_date(item['date_to']),
                org=Org.get(org_id=item['org']['id']) if item.get('org') else None,
                pay_method=item['pay_method'],
                exam_type=item['exam_type'],
                post=item['post'],
                shop=item['shop'],
            ))
        return directions

    @classmethod
    def get(cls, direction_id) -> 'Direction':
        url = settings.MIS_URL + f'/api/pre_record/{direction_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        result = response.json()
        direction = cls(
            number=result['id'],
            last_name=result['last_name'],
            first_name=result['first_name'],
            middle_name=result['middle_name'],
            birth=iso_to_date(result['birth']),
            gender=result['gender'],
            from_date=iso_to_date(result['date_from']),
            to_date=iso_to_date(result['date_to']),
            org=Org.get(org_id=result['org']['id']) if result.get('org') else None,
            pay_method=result['pay_method'],
            exam_type=result['exam_type'],
            post=result['post'],
            shop=result['shop'],
        )
        return direction
