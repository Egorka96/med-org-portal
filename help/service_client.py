import requests
from django.conf import settings


class Help:
    ARTICLE_LIST_URL = '/api/article/'

    def __init__(self):
        self.url = settings.HELP_URL
        self._status = None

    def request(self, path, params=None, data=None, method='get'):
        assert method in ('get', 'post')

        url = settings.MIS_URL + path
        headers = {'Authorization': f'Token {settings.MIS_TOKEN}'}

        response = requests.request(method=method, url=url, headers=headers, params=params, data=data)
        response.raise_for_status()

        return response.json()
