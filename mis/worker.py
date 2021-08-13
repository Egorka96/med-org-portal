import datetime
from dataclasses import dataclass
from typing import Dict, List

from djutils.date_utils import iso_to_date

from mis.document import Document
from mis.law_item import LawItem
from mis.org import Org
from mis.service_client import Mis


@dataclass
class Worker:
    id: int
    org: Org
    last_name: str
    first_name: str
    birth: datetime.date
    gender: str

    middle_name: str = None
    post: str = None
    shop: str = None
    law_items: List[LawItem] = None

    documents: List[Document] = None

    def __str__(self):
        return ' '.join(filter(bool, [self.last_name, self.first_name, self.middle_name]))

    @classmethod
    def filter_with_response(cls, params: Dict = None, user: 'core.models.DjangoUser' = None):
        response_json = Mis().request(path='/api/workers/', params=params, user=user)

        workers = []
        for item in response_json['results']:
            workers.append(cls.get_from_dict(item))

        response_json['results'] = workers
        return response_json

    @classmethod
    def filter(cls, params: Dict = None, user=None) -> List['Worker']:
        return cls.filter_with_response(params, user=user)['results']

    @classmethod
    def get(cls, worker_id, user=None) -> 'Worker':
        result = Mis().request(path=f'/api/workers/{worker_id}/')
        worker = cls.get_from_dict(result, user)
        return worker

    @classmethod
    def get_from_dict(cls, data: dict, user=None) -> 'Worker':
        if data.get('visits'):
            available_document_type_ids = user.core.available_document_type_ids.values_list('document_type_id', flat=True)\
                                            if user else []

            data['documents'] = []
            for date_data in data['visits']:
                for document_data in date_data.get('documents', []):
                    if document_data['doc_type']['id'] not in available_document_type_ids:
                        continue
                    document_data['date'] = iso_to_date(date_data['date'])
                    data['documents'].append(Document.get_from_dict(document_data))

        return cls(
            id=data['id'],
            last_name=data['last_name'],
            first_name=data['first_name'],
            middle_name=data['middle_name'],
            birth=iso_to_date(data['birth']),
            gender=data['gender'],
            org=Org.get_from_dict(data=data['org']) if data.get('org') else None,
            post=data['post'],
            shop=data['shop'],
            law_items=[LawItem.get_from_dict(l_i) for l_i in data.get('law_items', [])],
            documents=data.get('documents')
        )
