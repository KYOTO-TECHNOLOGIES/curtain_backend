from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import WorkType


class CatalogApiTests(APITestCase):
    def test_work_types_list_endpoint(self):
        WorkType.objects.create(name="Roller", pricing_unit="m2")

        response = self.client.get(reverse("work-type-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Roller")
