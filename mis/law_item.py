from dataclasses import dataclass, asdict
from typing import List, Dict

import requests
from django.conf import settings
from mis.service_client import Mis


@dataclass
class Law:
    id: int
    name: str

    @classmethod
    def get_from_dict(cls, data: dict) -> 'Law':
        return cls(
            id=data['id'],
            name=data['name'],
        )


@dataclass
class LawItem:
    id: int
    name: str
    section: str
    law: Law
    description: str
    display: str

    def __str__(self):
        return self.display

    @classmethod
    def filter_raw(cls, params: Dict = None):
        response_json = Mis().request(path='/api/law_items/', params=params)

        law_item = []
        for item in response_json['results']:
            law_item.append(asdict(cls.get_from_dict(item)))

        response_json['results'] = law_item
        return response_json

    @classmethod
    def filter(cls, params: Dict = None) -> List['LawItem']:
        response_json = Mis().request(path='/api/law_items/', params=params)

        law_items = []
        for item in response_json['results']:
            law_items.append(cls.get_from_dict(item))
        return law_items

    @classmethod
    def get(cls, law_item_id: int) -> 'LawItem':
        result = Mis().request(path=f'/api/law_items/{law_item_id}/')
        return cls.get_from_dict(result)

    @classmethod
    def get_from_dict(cls, data: dict) -> 'LawItem':
        return cls(
            id=data['id'],
            name=data['name'],
            section=data['section'],
            law=Law.get_from_dict(data['law']),
            description=data.get('description'),
        )
