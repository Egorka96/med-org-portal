from typing import List
from dataclasses import dataclass
import requests
from django.conf import settings


@dataclass
class PayMethod:
    id: int
    name: str
    type: str

    def __str__(self):
        return self.name

    @classmethod
    def filter(cls) -> List['PayMethod']:
        url = settings.MIS_URL + f'/api/pay_methods/'
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}
        response = requests.get(url=url, headers=headers)
        response.raise_for_status()

        pay_methods = []
        for item in response.json():
            pay_methods.append(cls(
                id=item['id'],
                name=item['name'],
                type=item['type'],
            ))
        return pay_methods
