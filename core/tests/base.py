from collections import Iterable

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class BaseTestCase(TestCase):
    view = None
    permission = None
    any_permissions = None
    need_auth = True

    SUCCESS_OPEN_CODE = 200
    REDIRECT_CODE = 302

    username = 'test'
    password = 'testtest'

    def setUp(self):
        self.create_user()
        self.generate_data()
        self.check_open()

        if self.need_auth:
            self.check_auth()

    def get_permission(self):
        return self.permission

    def get_any_permissions(self):
        return self.any_permissions

    def generate_data(self):
        pass

    def user_config(self):
        perms = []
        if self.get_permission():
            perms.append(self.get_permission().split('.'))
        elif self.get_any_permissions():
            perms.extend([perm.split('.') for perm in self.get_any_permissions()])

        for app_label, codename in perms:
            self.user.user_permissions.add(
                Permission.objects.get(content_type__app_label=app_label, codename=codename)
            )

    def create_user(self):
        self.user = User.objects.create(
            username=self.username,
            password=self.password,
        )
        self.user_config()
        self.client.force_login(self.user)

    def get_url_params(self):
        return {}

    def get_url_args(self):
        return []

    def get_url_kwargs(self):
        return {}

    def get_url(self):
        return reverse(self.view, args=self.get_url_args(), kwargs=self.get_url_kwargs())

    def check_open(self):
        response = self.client.get(self.get_url(), data=self.get_url_params(), follow=True)
        self.assertEqual(response.status_code, self.SUCCESS_OPEN_CODE)

    def check_auth(self):
        self.client.logout()
        response = self.client.get(self.get_url(), data=self.get_url_params(), follow=True)
        redirect_url = response.request['PATH_INFO']
        self.assertEqual('/login/', redirect_url)

        self.client.force_login(self.user)

        response = self.client.get(self.get_url(), data=self.get_url_params(), follow=True)
        redirect_url = response.request['PATH_INFO']
        self.assertNotEqual('/login/', redirect_url)

        if self.get_permission() or self.get_any_permissions():
            self.check_permission()

        response = self.client.get(self.get_url(), data=self.get_url_params(), follow=True)
        url = response.request['PATH_INFO']
        self.assertEqual(url, self.get_url())
        self.assertEqual(response.status_code, self.SUCCESS_OPEN_CODE)

    def check_permission(self):
        self.user.user_permissions.clear()
        response = self.client.get(self.get_url(),  data=self.get_url_params(), follow=True)
        self.assertEqual(response.status_code, 403)
        if self.get_permission():
            app_label, codename = self.get_permission().split('.')
            self.user.user_permissions.add(
                Permission.objects.get(content_type__app_label=app_label, codename=codename)
            )
        else:
            for perm in self.get_any_permissions():
                app_label, codename = perm.split('.')
                self.user.user_permissions.add(
                    Permission.objects.get(content_type__app_label=app_label, codename=codename)
                )

        response = self.client.get(self.get_url(), data=self.get_url_params(), follow=True)
        url = response.request['PATH_INFO']
        self.assertEqual(response.status_code, self.SUCCESS_OPEN_CODE)

    def check_response(self, response, status=200, url=None):

        if url is None:
            url = self.get_url()

        self.assertEqual(response.status_code, status, response)
        self.assertEqual(response.request['PATH_INFO'], url)

    def check_context(self, response, key, value):
        self.assertIn(key, response.context)

        response_data = response.context[key]
        if isinstance(value, Iterable):
            self.assertEqual(len(response_data), len(value))
            for obj in value:
                self.assertIn(obj, response_data)
        else:
            self.assertEqual(response_data, value)
