from dataclasses import dataclass
from typing import List, Dict

import requests
from django.conf import settings


@dataclass
class DocumentType:
    id: int
    name: str

    def __str__(self):
        return self.name

    @classmethod
    def filter(cls, params: Dict = None) -> List['DocumentType']:
        url = settings.MIS_URL + f'/api/document_type/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        document_types = []
        for item in response.json():
            document_types.append(cls.get_from_dict(item))
        return document_types

    @classmethod
    def get(cls, document_type_id) -> 'DocumentType':
        url = settings.MIS_URL + f'/api/document_type/{document_type_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        result = response.json()
        return cls.get_from_dict(result)

    @classmethod
    def get_from_dict(cls, data) -> 'DocumentType':
        return cls(
            id=data['id'],
            name=data.get('name'),
        )