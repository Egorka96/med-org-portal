from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from core.tests.base import BaseTestCase
from core import models

User = get_user_model()


class TestDelete(BaseTestCase):
    view = 'core:user_delete'
    permission = 'auth.delete_user'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

        self.test_user = User.objects.create(
            username='new_user',
            password='123456'
        )
        self.test_mis_user = models.User.objects.create(django_user=self.test_user)

    def get_url_kwargs(self):
        return {'pk': self.test_mis_user.id}

    def test_delete(self):
        response = self.client.get(self.get_url())
        self.check_response(response)
        self.assertEqual(response.context_data['object'], self.test_user)

        users = User.objects.all()
        self.assertIn(self.test_user, users)

        response = self.client.delete(self.get_url())
        self.check_response(response, status=302)
        self.assertEqual(response.url, reverse_lazy('core:user'))

        users = User.objects.all()
        self.assertNotIn(self.test_user, users)
