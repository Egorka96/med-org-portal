import datetime
from dataclasses import dataclass
from typing import List, Dict

from help.service_client import Help


@dataclass
class Article:
    id: int
    name: str
    service: int
    section: int
    tags: [int]

    short_description: str
    text: str
    sort_priority: int
    dc: datetime.datetime
    dm: datetime.datetime

    @classmethod
    def dict_to_obj(cls, data: dict) -> 'Article':
        return cls(
            id=data['id'],
            name=data['name'],
            service=data['service'],
            section=data['section'],
            tags=data['tags'],
            short_description=data.get('short_description'),
            text=data.get('text'),
            sort_priority=data['sort_priority'],
            dc=data['dc'],
            dm=data['dm']
        )

    @classmethod
    def filter(cls, params: Dict = None) -> List['Article']:
        articles = []
        page = 1

        while True:
            params['page'] = page
            response_json = Help().request(path='/api/article/', params=params)
            for item in response_json['results']:
                articles.append(cls.dict_to_obj(item))
            if not response_json.get('next'):
                break
            page += 1

        return articles

    @classmethod
    def get(cls, article_id) -> 'Article':
        result = Help().request(path=f'/api/article/{article_id}/')
        article = cls.dict_to_obj(result)
        return article
