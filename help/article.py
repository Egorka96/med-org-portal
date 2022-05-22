import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict

from help.service_client import Help


@dataclass
class Article:
    id: int
    name: str
    section: int
    sort_priority: int

    short_description: str = None
    text: str = None

    @classmethod
    def dict_to_obj(cls, data: dict) -> 'Article':
        return cls(
            id=data['id'],
            name=data['name'],
            section=data['section'],
            sort_priority=data['sort_priority'],
            short_description=data.get('short_description'),
            text=data.get('text'),
        )

    @classmethod
    def filter_raw(cls, params: Dict = None):
        response_json = Help().request(path='/api/article/', params=params)

        articles = []
        for item in response_json['results']:
            articles.append(asdict(cls.dict_to_obj(item)))
        response_json['results'] = articles

        return response_json
