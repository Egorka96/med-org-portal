import json
from dataclasses import dataclass, asdict
from typing import List, Dict

from mis.service_client import Mis


@dataclass
class Org:
    id: int
    name: str
    legal_name: str = None

    def __str__(self):
        return self.legal_name or self.name

    @classmethod
    def filter_raw(cls, params: Dict = None, user: 'core.models.DjangoUser' = None):
        if user:
            params = params or {}
            params['id'] = json.loads(user.core.org_ids)

        response_json = Mis().request(path='/api/orgs/', params=params, user=user)

        orgs = []
        for item in response_json['results']:
            orgs.append(asdict(cls.get_from_dict(item)))

        response_json['results'] = orgs
        return response_json

    @classmethod
    def filter(cls, params: Dict = None, user: 'core.models.DjangoUser' = None) -> List['Org']:
        if user:
            params = params or {}
            params['id'] = json.loads(user.core.org_ids)

        response_json = Mis().request(path='/api/orgs/', params=params, user=user)

        orgs = []
        for item in response_json['results']:
            orgs.append(cls.get_from_dict(item))
        return orgs

    @classmethod
    def get(cls, org_id) -> 'Org':
        result = Mis().request(path= f'/api/orgs/{org_id}/')
        return cls.get_from_dict(result)

    @classmethod
    def get_from_dict(cls, data) -> 'Org':
        org = cls(
            id=data['id'],
            name=data.get('name'),
            legal_name=data['legal_name'],
        )
        return org