import json
from unittest import mock

from django.contrib.auth.models import Permission as AuthPermission
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth import get_user_model

from django.urls import reverse_lazy

from core import models
from core.mis.org import Org
from core.tests.base import BaseTestCase

User = get_user_model()


class TestAdd(BaseTestCase):
    view = 'core:user_add'
    permission = 'auth.add_user'

    def generate_data(self):
        self.core_user = models.User.objects.create(django_user=self.user)

        self.permission_group = AuthGroup.objects.create(name='Testing permission group')
        self.auth_permission = AuthPermission.objects.get(id=1)
        self.permission_group.permissions.add(self.auth_permission)

    @mock.patch.object(Org, 'get')
    def test_add(self, mock_org):
        mock_org.return_value = Org(id=1, name='test org')

        users_count = User.objects.count()
        self.assertEqual(users_count, 1)

        core_users_count = models.User.objects.count()
        self.assertEqual(core_users_count, 1)

        params = {
            'username': 'NewUser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@tes.ru',
            'is_active': True,
            'new_password': '123456',
            'groups': self.permission_group.id,
            'orgs': ["1", "5", "8"]
        }
        response = self.client.post(self.get_url(), params)
        self.check_response(response, status=302)
        self.assertEqual(response.url, reverse_lazy('core:user'))

        user = User.objects.all()[1]
        self.assertEqual(user.username, params['username'])

        core_user = models.User.objects.all()[1]
        self.assertEqual(core_user.django_user, user)
        self.assertEqual(core_user.org_ids, json.dumps(params['orgs']))

    def test_add_errors(self):
        params = {
            'username': '',
        }
        response = self.client.post(self.get_url(), params)
        self.check_response(response, status=200)
        self.assertEqual(['Это поле обязательно.'], response.context_data['form'].errors['username'])
