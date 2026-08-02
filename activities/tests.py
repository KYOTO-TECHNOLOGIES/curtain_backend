from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework.test import APITestCase

from catalog.models import WorkType
from .models import ActivityLog


class ActivitiesApiTests(APITestCase):
    def test_activity_logs_list_endpoint(self):
        user = get_user_model().objects.create_user(
            email="activity@example.com",
            password="secret123",
            full_name="Activity User",
        )
        work_type = WorkType.objects.create(name="Roman", pricing_unit="m2")

        ActivityLog.objects.create(
            action="created",
            details={"source": "test"},
            content_type=ContentType.objects.get_for_model(WorkType),
            object_id=work_type.id,
            user=user,
        )

        response = self.client.get(reverse("activity-log-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["action"], "created")
