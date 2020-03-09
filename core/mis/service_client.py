from typing import Optional

import requests
from django.conf import settings


class Mis:
    def __init__(self):
        self.url = settings.MIS_URL
        self._status = None

    def get_status(self) -> Optional[dict]:
        if self._status is None:
            url = self.url + '/api/status/'
            response = requests.get(url=url, headers={'Authorization': f'Token {settings.MIS_TOKEN}'}, timeout=5)
            response.raise_for_status()
            self._status = response.json()

        return self._status

    def is_out_used(self) -> bool:
        return self.get_status()['is_out_used']
