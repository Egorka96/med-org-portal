from core.tests.base import BaseRestTestCase
from django.urls import reverse
from rest_framework.test import APITestCase


class TessGeneratePasswordView(BaseRestTestCase, APITestCase):

    def generate_data(self):
        super().generate_data()
        self.url = reverse('core:rest_generate_password')

    def test_generate_password_view(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['password'])
