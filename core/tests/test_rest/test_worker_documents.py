from core.tests.base import BaseRestTestCase
from django.urls import reverse
from rest_framework.test import APITestCase


class TestWorkerDocuments(BaseRestTestCase, APITestCase):

    def generate_data(self):
        super().generate_data()
        self.url = reverse('core:rest_worker_documents')

    def get_mocked_worker_documents(self):
        pass
