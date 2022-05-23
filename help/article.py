import json
import datetime
from dataclasses import dataclass
from swutils.encrypt import encrypt
from urllib.parse import quote

from django.conf import settings
from typing import List, Dict

from help.service_client import Help

@dataclass
class Article:
    id: int
    name: str
    section: int
    sort_priority: int
    article_url: str

    short_description: str = None
    text: str = None

    @classmethod
    def dict_to_obj(cls, data: dict) -> 'Article':
        return cls(
            id=data['id'],
            name=data['name'],
            section=data['section'],
            sort_priority=data['sort_priority'],
            article_url=settings.HELP_URL + data['article_url'] + f'?token={cls.article_url_token()}',
            short_description=data.get('short_description'),
            text=data.get('text'),
        )

    @staticmethod
    def article_url_token():
        token_date = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=1), "%Y-%m-%d %H:%M")
        help_token_data = {
            'service_uuid': settings.HELP_SERVICE_UUID,
            'expired_time': token_date
        }
        help_token_data_dumped = json.dumps(help_token_data)
        token = encrypt(help_token_data_dumped, key=settings.HELP_ENCRYPT_TOKEN_KEY.encode()).decode()
        return str(quote(token))

    @classmethod
    def filter(cls, params: Dict = None) -> List['Article']:
        articles = []
        page = 1

        params['service_uuid'] = settings.HELP_SERVICE_UUID
        while True:
            params['page'] = page
            response_json = Help().request(path='/api/article/', params=params)
            for item in response_json['results']:
                articles.append(cls.dict_to_obj(item))
            if not response_json.get('next'):
                break
            page += 1

        return articles
