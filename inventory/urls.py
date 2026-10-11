from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'suppliers', views.SupplierViewSet, basename='inventory-supplier')
router.register(r'items', views.InventoryItemViewSet, basename='inventory-item')
router.register(r'movements', views.StockMovementViewSet, basename='inventory-movement')
router.register(r'reorders', views.ReorderRequestViewSet, basename='inventory-reorder')

urlpatterns = [
    path('', include(router.urls)),
]
