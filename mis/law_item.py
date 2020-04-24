from dataclasses import dataclass
from typing import List, Dict

import requests
from django.conf import settings


@dataclass
class LawItem:
    id: int
    name: str
    section: str
    description: str

    def __str__(self):
        return f'{self.name} прил.{self.section}'

    @classmethod
    def filter(cls, params: Dict = None) -> List['LawItem']:
        url = settings.MIS_URL + f'/api/law_items/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        law_items = []
        for item in response.json()['results']:
            law_items.append(cls.get_from_dict(item))
        return law_items

    @classmethod
    def get(cls, law_item_id: int) -> 'LawItem':
        url = settings.MIS_URL + f'/api/law_items/{law_item_id}'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        law_item_data = response.json()
        return cls.get_from_dict(law_item_data)

    @classmethod
    def get_from_dict(cls, data: dict) -> 'LawItem':
        return cls(
            id=data['id'],
            name=data['name'],
            section=data['section'],
            description=data.get('description'),
        )
