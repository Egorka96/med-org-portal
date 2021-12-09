import datetime
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

        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()

        document_types = []
        for item in response.json():
            document_types.append(cls.get_from_dict(item))
        return document_types

    @classmethod
    def get(cls, document_type_id) -> 'DocumentType':
        url = settings.MIS_URL + f'/api/document_type/{document_type_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()

        result = response.json()
        return cls.get_from_dict(result)

    @classmethod
    def get_from_dict(cls, data) -> 'DocumentType':
        return cls(
            id=data['id'],
            name=data.get('name'),
        )


@dataclass
class Document:
    date: datetime.date
    document_type: DocumentType
    document_link: str

    @classmethod
    def get_from_dict(cls, data) -> 'Document':
        return cls(
            date=data['date'],
            document_type=DocumentType.get_from_dict(data['doc_type']),
            document_link=data['doc_link'],
        )

    @classmethod
    def get_choices(cls, filter_params_str: str) -> List[Dict]:
        url = settings.MIS_URL + '/api/document/builder/choices/?' + filter_params_str
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()

        response_json = response.json()
        results = []
        for item in response_json:
            results.append({
                'doc_type': DocumentType.get_from_dict(item['doc_type']),
                'doc_link': item['link']
            })
        return results

    @classmethod
    def get_content(cls, path: str) -> bytes:
        url = settings.MIS_URL + path
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()
        return response.content
