import requests
from django.conf import settings


class Help:
    ARTICLE_LIST_URL = '/api/article/'

    def request(self, path, params=None, data=None, method='get'):
        assert method in ('get', 'post')

        url = settings.HELP_URL + path
        headers = {'Authorization': f'Token {settings.HELP_TOKEN}'}

        response = requests.request(method=method, url=url, headers=headers, params=params, data=data)
        response.raise_for_status()

        return response.json()
