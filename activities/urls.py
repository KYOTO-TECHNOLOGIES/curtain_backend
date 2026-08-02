from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"activity-logs", views.ActivityLogViewSet, basename="activity-log")

urlpatterns = [
    path("", include(router.urls)),
]
