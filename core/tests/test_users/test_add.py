import json
from unittest import mock

from django.contrib.auth.models import Permission as AuthPermission
from django.contrib.auth.models import Group as AuthGroup
from django.contrib.auth import get_user_model

from django.urls import reverse_lazy

from mis.org import Org
from mis.document import DocumentType

from core import models
from core.tests.base import BaseTestCase

User = get_user_model()


class TestAdd(BaseTestCase):
    view = 'core:user_add'
    permission = 'auth.add_user'

    @mock.patch.object(Org, 'get')
    @mock.patch.object(DocumentType, 'filter')
    def setUp(self, mock_document_type, mock_org):
        mock_document_type.return_value = [
            DocumentType(id=1, name='Тестовый документ1'),
            DocumentType(id=2, name='Тестовый документ2'),
        ]
        mock_org.return_value = Org(id=1, name='test org')
        super().setUp()

    def generate_data(self):
        self.permission_group = AuthGroup.objects.create(name='Testing permission group')
        self.auth_permission = AuthPermission.objects.get(id=1)
        self.permission_group.permissions.add(self.auth_permission)

    @mock.patch.object(Org, 'get')
    @mock.patch.object(DocumentType, 'filter')
    def test_add(self, mock_document_type, mock_org):
        mock_document_type.return_value = [
            DocumentType(id=1, name='Тестовый документ1'),
            DocumentType(id=2, name='Тестовый документ2'),
        ]
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
            'new_password': '123456йцукен',
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

    @mock.patch.object(Org, 'get')
    @mock.patch.object(DocumentType, 'filter')
    def test_add_errors(self, mock_document_type, mock_org):
        mock_document_type.return_value = [
            DocumentType(id=1, name='Тестовый документ1'),
            DocumentType(id=2, name='Тестовый документ2'),
        ]
        mock_org.return_value = Org(id=1, name='test org')

        params = {
            'username': '',
        }
        response = self.client.post(self.get_url(), params)
        self.check_response(response, status=200)
        self.assertEqual(['Это поле обязательно.'], response.context_data['form'].errors['username'])
