from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"work-types", views.WorkTypeViewSet, basename="work-type")
router.register(r"fabric-types", views.FabricTypeViewSet, basename="fabric-type")
router.register(r"models", views.ModelViewSet, basename="model")
router.register(r"items", views.CatalogItemViewSet, basename="catalog-item")
router.register(r"motors", views.MotorTypeViewSet, basename="motor-type")
router.register(r"charges", views.ChargeTemplateViewSet, basename="charge-template")

urlpatterns = [
    path("", include(router.urls)),
]
