from django.contrib.auth import get_user_model

from core.tests.base import BaseTestCase
from core import models

User = get_user_model()


class TestSearch(BaseTestCase):
    view = 'core:user'
    permission = 'auth.view_user'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

        self.test_user = User.objects.create(
            username='new_user',
            last_name='test_human',
            password='123456'
        )
        self.test_core_user = models.User.objects.create(django_user=self.test_user)

        self.test_user2 = User.objects.create(
            username='testuser',
            last_name='newtest',
            password='123456'
        )
        self.test_core_user2 = models.User.objects.create(django_user=self.test_user2)

    def test_search_by_last_name(self):
        params = {'last_name': 'test_'}
        response = self.client.get(self.get_url(), params)
        self.check_response(response)
        self.assertEqual([self.test_user], list(response.context_data['object_list']))

    def test_search_by_username(self):
        params = {'username': 'testuser'}
        response = self.client.get(self.get_url(), params)
        self.check_response(response)
        self.assertEqual([self.test_user2], list(response.context_data['object_list']))
