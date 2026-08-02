from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'phone', 'email',
            'address_line_1', 'address_line_2', 'city', 'state', 'postal_code',
            'country', 'company_name', 'notes',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.full_name
    
    def validate_phone(self, value):
        if value and Customer.objects.exclude(id=self.instance.id if self.instance else None).filter(phone=value).exists():
            raise serializers.ValidationError("A customer with this phone already exists.")
        return value
    
    def validate_email(self, value):
        if value and Customer.objects.exclude(id=self.instance.id if self.instance else None).filter(email__iexact=value).exists():
            raise serializers.ValidationError("A customer with this email already exists.")
        return value