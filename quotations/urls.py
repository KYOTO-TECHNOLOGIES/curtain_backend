from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.QuotationViewSet, basename='quotation')

# The router automatically registers these URLs:
# /api/quotations/ - GET (list), POST (create)
# /api/quotations/{id}/ - GET, PUT, PATCH, DELETE
# /api/quotations/{id}/status/ - PATCH
# /api/quotations/{id}/duplicate/ - POST
# /api/quotations/{id}/send/ - PATCH
# /api/quotations/{id}/accept/ - PATCH
# /api/quotations/{id}/cancel/ - PATCH
# /api/quotations/stats/ - GET

urlpatterns = [
    path('', include(router.urls)),
]