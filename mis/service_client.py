import json
from typing import Optional

import requests
from django.conf import settings


class Mis:
    WORKERS_DONE_REPORT_URL = '/api/orders/by_client_date/'
    DIRECTIONS_LIST_URL = '/api/pre_record/'

    def __init__(self):
        self.url = settings.MIS_URL
        self._status = None

    def get_status(self) -> Optional[dict]:
        if self._status is None:
            url = self.url + '/api/status/'
            response = requests.get(url=url, headers={'Authorization': f'Token {settings.MIS_TOKEN}'})
            response.raise_for_status()
            self._status = response.json()

        return self._status

    def is_out_used(self) -> bool:
        return self.get_status()['is_out_used']

    def get_response(self, path, request, params = None, method='get'):
        assert method in ('get', 'post')

        if params and request.user.core.org_ids and not params.get('orgs'):
            params.update({
                'orgs': json.loads(request.user.core.org_ids)
            })

        url = settings.MIS_URL + path
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.request(method, url=url, headers=headers, params=params)
        response.raise_for_status()

        return response.json()
