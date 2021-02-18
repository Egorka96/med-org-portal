from dataclasses import dataclass
from typing import List, Dict

import requests
from django.conf import settings


@dataclass
class Org:
    id: int
    name: str
    legal_name: str = None

    def __str__(self):
        return self.legal_name or self.name

    @classmethod
    def filter(cls, params: Dict = None) -> List['Org']:
        url = settings.MIS_URL + f'/api/orgs/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()

        orgs = []
        for item in response.json()['results']:
            orgs.append(cls.get_from_dict(item))
        return orgs

    @classmethod
    def get(cls, org_id) -> 'Org':
        url = settings.MIS_URL + f'/api/orgs/{org_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()

        result = response.json()
        return cls.get_from_dict(result)

    @classmethod
    def get_from_dict(cls, data) -> 'Org':
        org = cls(
            id=data['id'],
            name=data.get('name'),
            legal_name=data['legal_name'],
        )
        return org