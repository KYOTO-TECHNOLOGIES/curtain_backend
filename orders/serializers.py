from rest_framework import serializers
from django.db import transaction,models  
from decimal import Decimal
from django.utils import timezone
from .models import Order, Invoice, Payment
from quotations.models import Quotation
from customers.models import Customer
from users.models import User


class PaymentSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    invoice_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number',
            'amount', 'method', 'reference',
            'payment_date', 'notes',
            'created_by', 'created_by_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.full_name or obj.created_by.email if obj.created_by else None
    
    def get_invoice_number(self, obj):
        return obj.invoice.id if obj.invoice else None


class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'invoice', 'amount', 'method',
            'reference', 'payment_date', 'notes'
        ]
    
    def validate(self, data):
        invoice = data.get('invoice')
        amount = data.get('amount')
        
        if amount <= 0:
            raise serializers.ValidationError({
                'amount': 'Payment amount must be greater than zero.'
            })
        
        # Check if payment exceeds invoice balance
        if invoice:
            total_paid = invoice.payments.aggregate(total=models.Sum('amount'))['total'] or 0
            balance = invoice.total_amount - total_paid
            if amount > balance:
                raise serializers.ValidationError({
                    'amount': f'Payment amount cannot exceed invoice balance of {balance}.'
                })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        payment = Payment.objects.create(**validated_data)
        
        # Update invoice status
        invoice = payment.invoice
        total_paid = invoice.payments.aggregate(total=models.Sum('amount'))['total'] or 0
        
        if total_paid >= invoice.total_amount:
            invoice.status = 'paid'
        else:
            invoice.status = 'partially_paid'
        invoice.amount_paid = total_paid
        invoice.save()
        
        return payment


class InvoiceSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    customer_email = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()
    quotation_id = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'order', 'order_id',
            'customer', 'customer_name', 'customer_phone', 'customer_email',
            'status', 'status_display',
            'total_amount', 'amount_paid', 'balance_due',
            'due_date', 'issued_date',
            'payment_terms', 'payment_url',
            'sent_date', 'sent_via',
            'quotation_id',
            'payments',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'issued_date', 'created_at', 'updated_at',
            'amount_paid', 'balance_due'
        ]
    
    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else ''
    
    def get_customer_phone(self, obj):
        return obj.customer.phone if obj.customer else ''
    
    def get_customer_email(self, obj):
        return obj.customer.email if obj.customer else ''
    
    def get_order_id(self, obj):
        return obj.order.id if obj.order else None
    
    def get_quotation_id(self, obj):
        return obj.order.quotation.id if obj.order and obj.order.quotation else None
    
    def get_balance_due(self, obj):
        return obj.total_amount - obj.amount_paid
    
    def get_status_display(self, obj):
        status_map = {
            'draft': 'Draft',
            'sent': 'Sent',
            'overdue': 'Overdue',
            'paid': 'Paid',
            'partially_paid': 'Partially Paid'
        }
        return status_map.get(obj.status, obj.status)


class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'order', 'customer', 'total_amount',
            'due_date', 'payment_terms', 'payment_url'
        ]
        read_only_fields = ['id', 'issued_date']
    
    def validate(self, data):
        order = data.get('order')
        
        # Check if invoice already exists for this order
        if order and hasattr(order, 'invoice'):
            raise serializers.ValidationError({
                'order': 'An invoice already exists for this order.'
            })
        
        # Check if total amount is valid
        if data.get('total_amount', 0) <= 0:
            raise serializers.ValidationError({
                'total_amount': 'Total amount must be greater than zero.'
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        validated_data['status'] = 'draft'
        invoice = Invoice.objects.create(**validated_data)
        return invoice


class InvoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'status', 'payment_terms', 'payment_url',
            'due_date', 'sent_via'
        ]
    
    def validate(self, data):
        if data.get('status') == 'paid':
            # Check if payments cover the total amount
            invoice = self.instance
            total_paid = invoice.payments.aggregate(total=models.Sum('amount'))['total'] or 0
            if total_paid < invoice.total_amount:
                raise serializers.ValidationError({
                    'status': 'Cannot mark as paid. Payments do not cover the full amount.'
                })
        return data


class InvoiceStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Invoice.STATUS_CHOICES, required=True)
    sent_via = serializers.CharField(required=False, allow_blank=True)

class OrderSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    customer_phone = serializers.SerializerMethodField()
    quotation_id = serializers.SerializerMethodField()
    invoice_id = serializers.SerializerMethodField()
    invoice_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 
            'quotation', 
            'quotation_id',  # This must be here
            'customer', 
            'customer_name', 
            'customer_phone',
            'order_status',
            'estimated_production_days',
            'invoice', 
            'invoice_id', 
            'invoice_status',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_customer_name(self, obj):
        return obj.customer.full_name if obj.customer else ''
    
    def get_customer_phone(self, obj):
        return obj.customer.phone if obj.customer else ''
    
    def get_quotation_id(self, obj):
        return obj.quotation.id if obj.quotation else None
    
    def get_invoice_id(self, obj):
        return obj.invoice.id if hasattr(obj, 'invoice') else None
    
    def get_invoice_status(self, obj):
        if hasattr(obj, 'invoice'):
            return obj.invoice.status
        return None

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'quotation', 'customer',
            'order_status', 'estimated_production_days'
        ]
    
    def validate(self, data):
        quotation = data.get('quotation')
        
        # Check if quotation is accepted
        if quotation and quotation.status != 'accepted':
            raise serializers.ValidationError({
                'quotation': 'Order can only be created from accepted quotations.'
            })
        
        # Check if order already exists for this quotation
        if quotation and Order.objects.filter(quotation=quotation).exists():
            raise serializers.ValidationError({
                'quotation': 'An order already exists for this quotation.'
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        return order


class OrderStatusUpdateSerializer(serializers.Serializer):
    order_status = serializers.ChoiceField(choices=Order.STATUS_CHOICES, required=True)


class OrderStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_status = serializers.DictField()
    pending_production = serializers.IntegerField()
    in_production = serializers.IntegerField()
    shipped = serializers.IntegerField()
    installed = serializers.IntegerField()
    closed = serializers.IntegerField()


class InvoiceStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_status = serializers.DictField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_due = serializers.DecimalField(max_digits=12, decimal_places=2)
    overdue = serializers.IntegerField()