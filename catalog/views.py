from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import WorkType, FabricType, Model, CatalogItem, MotorType, ChargeTemplate
from .serializers import (
    WorkTypeSerializer,
    FabricTypeSerializer,
    ModelSerializer,
    CatalogItemSerializer,
    MotorTypeSerializer,
    ChargeTemplateSerializer,
)


class WorkTypeViewSet(viewsets.ModelViewSet):
    queryset = WorkType.objects.all()
    serializer_class = WorkTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class FabricTypeViewSet(viewsets.ModelViewSet):
    queryset = FabricType.objects.select_related("work_type").all()
    serializer_class = FabricTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ModelViewSet(viewsets.ModelViewSet):
    queryset = Model.objects.select_related("fabric_type", "fabric_type__work_type").all()
    serializer_class = ModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CatalogItemViewSet(viewsets.ModelViewSet):
    queryset = CatalogItem.objects.select_related("model", "model__fabric_type", "model__fabric_type__work_type").all()
    serializer_class = CatalogItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class MotorTypeViewSet(viewsets.ModelViewSet):
    queryset = MotorType.objects.all()
    serializer_class = MotorTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ChargeTemplateViewSet(viewsets.ModelViewSet):
    queryset = ChargeTemplate.objects.all()
    serializer_class = ChargeTemplateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
