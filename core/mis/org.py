from dataclasses import dataclass
from typing import List, Dict

import requests
from django.conf import settings


@dataclass
class Org:
    id: int
    name: str
    legal_name: str

    def __str__(self):
        return self.name

    @classmethod
    def filter(cls, params: Dict = None) -> List['Org']:
        url = settings.MIS_URL + f'/api/orgs/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()

        orgs = []
        for item in response.json()['results']:
            orgs.append(cls(
                id=item['id'],
                name=item['name'],
                legal_name=item['legal_name'],
            ))
        return orgs

    @classmethod
    def get(cls, org_id) -> 'Org':
        url = settings.MIS_URL + f'/api/orgs/{org_id}/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        result = response.json()
        org = cls(
            id=result['id'],
            name=result['name'],
            legal_name=result['legal_name'],
        )
        return org