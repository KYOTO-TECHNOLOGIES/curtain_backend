from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from .models import Quotation, QuotationArea, QuotationSurface, SurfaceSpec
from customers.models import Customer
from appointments.models import Appointment
from catalog.models import WorkType, FabricType, Model as CatalogModel, CatalogItem, MotorType


class SurfaceSpecSerializer(serializers.ModelSerializer):
    fabric_type_name = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    catalog_item_name = serializers.SerializerMethodField()
    motor_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = SurfaceSpec
        fields = [
            'id', 'surface',
            'fabric_type', 'fabric_type_name',
            'model', 'model_name',
            'catalog_item', 'catalog_item_name',
            'fabric_code',
            'unit_price_per_m2',
            'fabric_total',
            'motor_control_type',
            'motor_type', 'motor_type_name',
            'motor_price_per_unit',
            'motor_charge_total',
            'manual_control_total',
            'smart_integration',
            'alexa_quantity',
            'alexa_unit_price',
            'alexa_total',
            'pelmet_enabled',
            'pelmet_width_cm',
            'pelmet_price_per_metre',
            'pelmet_total',
            'addon_label',
            'addon_amount',
            'line_item_total'
        ]
        read_only_fields = [
            'id', 'fabric_total', 'motor_charge_total', 
            'manual_control_total', 'alexa_total', 'pelmet_total',
            'line_item_total'
        ]
    
    def get_fabric_type_name(self, obj):
        return obj.fabric_type.name if obj.fabric_type else None
    
    def get_model_name(self, obj):
        return obj.model.name if obj.model else None
    
    def get_catalog_item_name(self, obj):
        return obj.catalog_item.name if obj.catalog_item else None
    
    def get_motor_type_name(self, obj):
        return obj.motor_type.name if obj.motor_type else None


class QuotationSurfaceSerializer(serializers.ModelSerializer):
    spec = SurfaceSpecSerializer(read_only=True)
    area_name = serializers.SerializerMethodField()
    
    class Meta:
        model = QuotationSurface
        fields = [
            'id', 'area', 'area_name',
            'surface_name',
            'surface_type',
            'width_cm',
            'height_cm',
            'calculated_area_m2',
            'opening_direction',
            'special_requirements',
            'sort_order',
            'spec'
        ]
        read_only_fields = ['id', 'calculated_area_m2']
    
    def get_area_name(self, obj):
        return obj.area.display_name if obj.area else None


class QuotationAreaSerializer(serializers.ModelSerializer):
    surfaces = QuotationSurfaceSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuotationArea
        fields = [
            'id', 'quotation',
            'area_type',
            'display_name',
            'sort_order',
            'surfaces'
        ]
        read_only_fields = ['id']


class QuotationListSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    appointment_id = serializers.SerializerMethodField()
    work_type_name = serializers.SerializerMethodField()
    prepared_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'customer', 'customer_name', 'customer_phone',
            'appointment', 'appointment_id',
            'status', 'quote_type',
            'work_type', 'work_type_name',
            'subtotal', 'vat', 'total',
            'discount_percentage', 'discount_amount',
            'valid_until', 'issued_date',
            'sent_date', 'sent_via',
            'prepared_by', 'prepared_by_name',
            'accepted_date',
            'created_at', 'updated_at'
        ]
    
    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else ''
    
    def get_customer_phone(self, obj):
        return obj.customer.phone if obj.customer else ''
    
    def get_appointment_id(self, obj):
        return obj.appointment.id if obj.appointment else None
    
    def get_work_type_name(self, obj):
        return obj.work_type.name if obj.work_type else ''
    
    def get_prepared_by_name(self, obj):
        return obj.prepared_by.full_name or obj.prepared_by.email if obj.prepared_by else None


class QuotationDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    appointment_id = serializers.SerializerMethodField()
    work_type_name = serializers.SerializerMethodField()
    prepared_by_name = serializers.SerializerMethodField()
    prepared_by_email = serializers.SerializerMethodField()
    areas = QuotationAreaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'customer', 'customer_name', 'customer_phone', 'customer_email',
            'appointment', 'appointment_id',
            'status', 'quote_type',
            'work_type', 'work_type_name',
            'subtotal', 'vat', 'total',
            'discount_percentage', 'discount_amount',
            'valid_until', 'issued_date',
            'sent_date', 'sent_via',
            'prepared_by', 'prepared_by_name', 'prepared_by_email',
            'accepted_date',
            'created_at', 'updated_at',
            'areas'
        ]
    
    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else ''
    
    def get_customer_phone(self, obj):
        return obj.customer.phone if obj.customer else ''
    
    def get_customer_email(self, obj):
        return obj.customer.email if obj.customer else ''
    
    def get_appointment_id(self, obj):
        return obj.appointment.id if obj.appointment else None
    
    def get_work_type_name(self, obj):
        return obj.work_type.name if obj.work_type else ''
    
    def get_prepared_by_name(self, obj):
        return obj.prepared_by.full_name or obj.prepared_by.email if obj.prepared_by else None
    
    def get_prepared_by_email(self, obj):
        return obj.prepared_by.email if obj.prepared_by else None


class QuotationCreateUpdateSerializer(serializers.ModelSerializer):
    areas_data = serializers.JSONField(write_only=True, required=False, help_text="Areas and surfaces data")
    areas = QuotationAreaSerializer(many=True, read_only=True)  # For response
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'customer', 'appointment',
            'status', 'quote_type',
            'work_type',
            'valid_until',
            'discount_percentage',
            'areas_data',
            'areas'
        ]
        read_only_fields = ['id', 'issued_date', 'created_at', 'updated_at']
    
    def validate(self, data):
        if data.get('discount_percentage') and data['discount_percentage'] > 100:
            raise serializers.ValidationError({
                'discount_percentage': 'Discount cannot exceed 100%.'
            })
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        areas_data = validated_data.pop('areas_data', [])
        validated_data.pop('prepared_by', None)
        
        quotation = Quotation.objects.create(
            **validated_data,
            prepared_by=self.context['request'].user
        )
        
        for area_data in areas_data:
            area = QuotationArea.objects.create(
                quotation=quotation,
                area_type=area_data.get('area_type', ''),
                display_name=area_data.get('display_name', ''),
                sort_order=area_data.get('sort_order', 0)
            )
            
            surfaces_data = area_data.get('surfaces', [])
            for surface_data in surfaces_data:
                surface = QuotationSurface.objects.create(
                    area=area,
                    surface_name=surface_data.get('surface_name', 'Surface 01'),
                    surface_type=surface_data.get('surface_type', 'window_curtain_path'),
                    width_cm=surface_data.get('width_cm', 0),
                    height_cm=surface_data.get('height_cm', 0),
                    opening_direction=surface_data.get('opening_direction', 'one_way'),
                    special_requirements=surface_data.get('special_requirements', ''),
                    sort_order=surface_data.get('sort_order', 0)
                )
                
                spec_data = surface_data.get('spec', {})
                if spec_data:
                    SurfaceSpec.objects.create(
                        surface=surface,
                        fabric_type_id=spec_data.get('fabric_type'),
                        model_id=spec_data.get('model'),
                        catalog_item_id=spec_data.get('catalog_item'),
                        fabric_code=spec_data.get('fabric_code', ''),
                        unit_price_per_m2=spec_data.get('unit_price_per_m2', 0),
                        motor_control_type=spec_data.get('motor_control_type', 'manual'),
                        motor_type_id=spec_data.get('motor_type'),
                        motor_price_per_unit=spec_data.get('motor_price_per_unit', 0),
                        smart_integration=spec_data.get('smart_integration', False),
                        alexa_quantity=spec_data.get('alexa_quantity', 0),
                        alexa_unit_price=spec_data.get('alexa_unit_price', 0),
                        pelmet_enabled=spec_data.get('pelmet_enabled', False),
                        pelmet_width_cm=spec_data.get('pelmet_width_cm', 0),
                        pelmet_price_per_metre=spec_data.get('pelmet_price_per_metre', 0),
                        addon_label=spec_data.get('addon_label', ''),
                        addon_amount=spec_data.get('addon_amount', 0)
                    )
        
        quotation.recalc_totals()
        return quotation
    
    @transaction.atomic
    def update(self, instance, validated_data):
        areas_data = validated_data.pop('areas_data', None)
        validated_data.pop('prepared_by', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if areas_data is not None:
            instance.areas.all().delete()
            
            for area_data in areas_data:
                area = QuotationArea.objects.create(
                    quotation=instance,
                    area_type=area_data.get('area_type', ''),
                    display_name=area_data.get('display_name', ''),
                    sort_order=area_data.get('sort_order', 0)
                )
                
                surfaces_data = area_data.get('surfaces', [])
                for surface_data in surfaces_data:
                    surface = QuotationSurface.objects.create(
                        area=area,
                        surface_name=surface_data.get('surface_name', 'Surface 01'),
                        surface_type=surface_data.get('surface_type', 'window_curtain_path'),
                        width_cm=surface_data.get('width_cm', 0),
                        height_cm=surface_data.get('height_cm', 0),
                        opening_direction=surface_data.get('opening_direction', 'one_way'),
                        special_requirements=surface_data.get('special_requirements', ''),
                        sort_order=surface_data.get('sort_order', 0)
                    )
                    
                    spec_data = surface_data.get('spec', {})
                    if spec_data:
                        SurfaceSpec.objects.create(
                            surface=surface,
                            fabric_type_id=spec_data.get('fabric_type'),
                            model_id=spec_data.get('model'),
                            catalog_item_id=spec_data.get('catalog_item'),
                            fabric_code=spec_data.get('fabric_code', ''),
                            unit_price_per_m2=spec_data.get('unit_price_per_m2', 0),
                            motor_control_type=spec_data.get('motor_control_type', 'manual'),
                            motor_type_id=spec_data.get('motor_type'),
                            motor_price_per_unit=spec_data.get('motor_price_per_unit', 0),
                            smart_integration=spec_data.get('smart_integration', False),
                            alexa_quantity=spec_data.get('alexa_quantity', 0),
                            alexa_unit_price=spec_data.get('alexa_unit_price', 0),
                            pelmet_enabled=spec_data.get('pelmet_enabled', False),
                            pelmet_width_cm=spec_data.get('pelmet_width_cm', 0),
                            pelmet_price_per_metre=spec_data.get('pelmet_price_per_metre', 0),
                            addon_label=spec_data.get('addon_label', ''),
                            addon_amount=spec_data.get('addon_amount', 0)
                        )
        
        instance.recalc_totals()
        return instance

class QuotationStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Quotation.STATUS_CHOICES, required=True)
    
    def validate(self, data):
        return data


class QuotationStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_status = serializers.DictField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    accepted_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    this_month = serializers.IntegerField()