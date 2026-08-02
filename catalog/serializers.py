from rest_framework import serializers

from .models import WorkType, FabricType, Model, CatalogItem, MotorType, ChargeTemplate


class WorkTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkType
        fields = ["id", "name", "pricing_unit", "features"]
        read_only_fields = ["id"]


class FabricTypeSerializer(serializers.ModelSerializer):
    work_type_name = serializers.CharField(source="work_type.name", read_only=True)

    class Meta:
        model = FabricType
        fields = ["id", "work_type", "work_type_name", "name"]
        read_only_fields = ["id"]


class ModelSerializer(serializers.ModelSerializer):
    fabric_type_name = serializers.CharField(source="fabric_type.name", read_only=True)

    class Meta:
        model = Model
        fields = ["id", "fabric_type", "fabric_type_name", "name"]
        read_only_fields = ["id"]


class CatalogItemSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source="model.name", read_only=True)

    class Meta:
        model = CatalogItem
        fields = ["id", "model", "model_name", "name", "price_per_unit", "image"]
        read_only_fields = ["id"]


class MotorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MotorType
        fields = ["id", "name", "price_per_m2"]
        read_only_fields = ["id"]


class ChargeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeTemplate
        fields = ["id", "name", "price", "unit"]
        read_only_fields = ["id"]
