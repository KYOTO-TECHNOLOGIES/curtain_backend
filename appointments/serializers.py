from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Appointment, AppointmentLocation
from customers.models import Customer
from customers.serializers import CustomerSerializer

User = get_user_model()


class AppointmentLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentLocation
        fields = [
            'id', 'building_name', 'unit_number', 'full_address',
            'coordinates', 'additional_instructions', 'location_status'
        ]
        read_only_fields = ['id']


class AppointmentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    assigned_to_name = serializers.SerializerMethodField()
    assigned_to_username = serializers.SerializerMethodField()
    location_full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'customer_name', 'customer_phone',
            'title', 'description', 'appointment_date', 'appointment_time', 'end_time',
            'job_type', 'status', 'assigned_to', 'assigned_to_name', 'assigned_to_username',
            'location_full_address', 'created_at', 'updated_at'
        ]
    
    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else ''
    
    def get_customer_phone(self, obj):
        return obj.customer.phone if obj.customer else ''
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.full_name or obj.assigned_to.email
        return None
    
    def get_assigned_to_username(self, obj):
        if obj.assigned_to:
            # Since USERNAME_FIELD is email, use email as username
            return obj.assigned_to.email
        return None
    
    def get_location_full_address(self, obj):
        if hasattr(obj, 'location'):
            return obj.location.full_address
        return None


class AppointmentDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    location = AppointmentLocationSerializer(read_only=True)
    assigned_to_name = serializers.SerializerMethodField()
    assigned_to_username = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    created_by_username = serializers.SerializerMethodField()
    cancelled_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'title', 'description',
            'appointment_date', 'appointment_time', 'end_time',
            'job_type', 'status', 'assigned_to', 'assigned_to_name', 'assigned_to_username',
            'created_by', 'created_by_name', 'created_by_username', 
            'created_at', 'updated_at',
            'cancellation_reason', 'cancelled_at', 'cancelled_by', 'cancelled_by_name',
            'location'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
            'cancelled_at', 'cancelled_by'
        ]
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.full_name or obj.assigned_to.email
        return None
    
    def get_assigned_to_username(self, obj):
        if obj.assigned_to:
            # Since USERNAME_FIELD is email, use email as username
            return obj.assigned_to.email
        return None
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name or obj.created_by.email
        return None
    
    def get_created_by_username(self, obj):
        if obj.created_by:
            return obj.created_by.email
        return None
    
    def get_cancelled_by_name(self, obj):
        if obj.cancelled_by:
            return obj.cancelled_by.full_name or obj.cancelled_by.email
        return None


class AppointmentCreateUpdateSerializer(serializers.ModelSerializer):
    # Customer fields
    customer_first_name = serializers.CharField(write_only=True, required=False)
    customer_last_name = serializers.CharField(write_only=True, required=False)
    customer_phone = serializers.CharField(write_only=True, required=False)
    customer_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    customer_address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_city = serializers.CharField(write_only=True, required=False, allow_blank=True)
    customer_source = serializers.CharField(write_only=True, required=False, default='walk_in')
    
    # Location fields
    location_building = serializers.CharField(write_only=True, required=False, allow_blank=True)
    location_unit = serializers.CharField(write_only=True, required=False, allow_blank=True)
    location_full_address = serializers.CharField(write_only=True, required=False, allow_blank=True)
    location_coordinates = serializers.JSONField(write_only=True, required=False, allow_null=True)
    location_instructions = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'customer', 'title', 'description',
            'appointment_date', 'appointment_time', 'end_time',
            'job_type', 'status', 'assigned_to',
            'customer_first_name', 'customer_last_name', 'customer_phone', 
            'customer_email', 'customer_address', 'customer_city', 'customer_source',
            'location_building', 'location_unit', 'location_full_address',
            'location_coordinates', 'location_instructions'
        ]
        read_only_fields = ['id', 'customer']
    
    def validate(self, data):
        if data.get('end_time') and data.get('appointment_time'):
            if data['end_time'] <= data['appointment_time']:
                raise serializers.ValidationError({
                    'end_time': 'End time must be after start time.'
                })
        return data
    
    def validate_assigned_to(self, value):
        if value:
            try:
                user = User.objects.get(id=value.id, is_active=True)
                # if user.role and user.role.name not in ['Admin', 'Salesman']:
                #     raise serializers.ValidationError("User must be a salesman or admin.")
                # return user
            except User.DoesNotExist:
                raise serializers.ValidationError("User does not exist.")
        return value
    
    def create(self, validated_data):
        extra_fields = [
            'customer_first_name', 'customer_last_name', 'customer_phone', 
            'customer_email', 'customer_address', 'customer_city', 'customer_source',
            'location_building', 'location_unit', 'location_full_address',
            'location_coordinates', 'location_instructions'
        ]
        
        for field in extra_fields:
            validated_data.pop(field, None)
        
        return Appointment.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        extra_fields = [
            'customer_first_name', 'customer_last_name', 'customer_phone', 
            'customer_email', 'customer_address', 'customer_city', 'customer_source',
            'location_building', 'location_unit', 'location_full_address',
            'location_coordinates', 'location_instructions'
        ]
        
        for field in extra_fields:
            validated_data.pop(field, None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AppointmentStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Appointment.STATUS_CHOICES, required=True)
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['status'] == 'cancelled' and not data.get('cancellation_reason'):
            raise serializers.ValidationError({
                'cancellation_reason': 'Reason is required when cancelling an appointment.'
            })
        return data


class AppointmentAssignSerializer(serializers.Serializer):
    assigned_to = serializers.IntegerField(required=True)
    
    def validate_assigned_to(self, value):
        try:
            user = User.objects.get(id=value, is_active=True)
            if user.role and user.role.name not in ['Admin', 'Salesman']:
                raise serializers.ValidationError("User must be a salesman or admin.")
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")