from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
from .models import Order, Invoice, Payment
from quotations.models import Quotation
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
    OrderStatsSerializer,
    InvoiceSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer,
    InvoiceStatusUpdateSerializer,
    InvoiceStatsSerializer,
    PaymentSerializer,
    PaymentCreateSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    Order ViewSet with full CRUD operations and custom actions.
    
    Provides:
    - list: GET /api/orders/
    - create: POST /api/orders/
    - retrieve: GET /api/orders/{id}/
    - update: PUT /api/orders/{id}/
    - partial_update: PATCH /api/orders/{id}/
    - destroy: DELETE /api/orders/{id}/
    
    Custom Actions:
    - status: PATCH /api/orders/{id}/status/
    - stats: GET /api/orders/stats/
    - generate_invoice: POST /api/orders/{id}/generate-invoice/
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.select_related('customer', 'quotation').all()
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderCreateSerializer
        elif self.action == 'list':
            return OrderSerializer
        else:
            return OrderSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(order_status=status_filter)
        
        # Filter by customer
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer_id=customer)
        
        # Filter by quotation
        quotation = self.request.query_params.get('quotation')
        if quotation:
            queryset = queryset.filter(quotation_id=quotation)
        
        # Search
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer__phone__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    def create(self, request, *args, **kwargs):
        """Create order and return with full serializer"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return with OrderSerializer instead of OrderCreateSerializer
        response_serializer = OrderSerializer(serializer.instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """
        Update order status.
        PATCH /api/orders/{id}/status/
        {
            "order_status": "in_production"
        }
        """
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_status = serializer.validated_data['order_status']
        order.order_status = new_status
        order.save()
        
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get order statistics.
        GET /api/orders/stats/
        """
        queryset = self.get_queryset()
        
        total = queryset.count()
        
        status_counts = {}
        for status_choice in Order.STATUS_CHOICES:
            status_code = status_choice[0]
            count = queryset.filter(order_status=status_code).count()
            if count > 0:
                status_counts[status_code] = count
        
        pending_production = queryset.filter(order_status='pending_production').count()
        in_production = queryset.filter(order_status='in_production').count()
        shipped = queryset.filter(order_status='shipped').count()
        installed = queryset.filter(order_status='installed').count()
        closed = queryset.filter(order_status='closed').count()
        
        return Response({
            'total': total,
            'by_status': status_counts,
            'pending_production': pending_production,
            'in_production': in_production,
            'shipped': shipped,
            'installed': installed,
            'closed': closed
        })
    
    @action(detail=True, methods=['post'], url_path='generate-invoice')
    def generate_invoice(self, request, pk=None):
        """
        Generate an invoice for an order.
        POST /api/orders/{id}/generate-invoice/
        """
        order = self.get_object()
        
        # Check if invoice already exists
        if hasattr(order, 'invoice'):
            return Response({
                'error': 'Invoice already exists for this order.',
                'invoice': InvoiceSerializer(order.invoice).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create invoice from order
        invoice = Invoice.objects.create(
            order=order,
            customer=order.customer,
            total_amount=order.quotation.total if order.quotation else 0,
            due_date=timezone.now().date() + timedelta(days=14),
            payment_terms='Full payment on invoice'
        )
        
        invoice_serializer = InvoiceSerializer(invoice)
        return Response(invoice_serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete - cancel order"""
        order = self.get_object()
        
        if order.order_status == 'closed':
            return Response({
                'error': 'Cannot delete a closed order.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if order has an invoice with payments
        if hasattr(order, 'invoice'):
            invoice = order.invoice
            if invoice.payments.exists():
                return Response({
                    'error': 'Cannot cancel order with payments. Void the payments first.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        order.order_status = 'cancelled'
        order.save()
        
        return Response({
            'message': f'Order {order.id} has been cancelled.',
            'order': OrderSerializer(order).data
        }, status=status.HTTP_200_OK)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    Invoice ViewSet with full CRUD operations and custom actions.
    
    Provides:
    - list: GET /api/invoices/
    - create: POST /api/invoices/
    - retrieve: GET /api/invoices/{id}/
    - update: PUT /api/invoices/{id}/
    - partial_update: PATCH /api/invoices/{id}/
    - destroy: DELETE /api/invoices/{id}/
    
    Custom Actions:
    - status: PATCH /api/invoices/{id}/status/
    - stats: GET /api/invoices/stats/
    - send: PATCH /api/invoices/{id}/send/
    - add-payment: POST /api/invoices/{id}/add-payment/
    """
    permission_classes = [IsAuthenticated]
    queryset = Invoice.objects.select_related('customer', 'order').prefetch_related('payments').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return InvoiceUpdateSerializer
        elif self.action == 'list':
            return InvoiceSerializer
        else:
            return InvoiceSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by customer
        customer = self.request.query_params.get('customer')
        if customer:
            queryset = queryset.filter(customer_id=customer)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(issued_date__gte=date_from)
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(issued_date__lte=date_to)
        
        # Search
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(customer__phone__icontains=search)
            )
        
        return queryset.order_by('-issued_date')
    
    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, pk=None):
        """
        Update invoice status.
        PATCH /api/invoices/{id}/status/
        {
            "status": "paid",
            "sent_via": "email"  // optional
        }
        """
        invoice = self.get_object()
        serializer = InvoiceStatusUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        new_status = serializer.validated_data['status']
        
        # Validate status transition
        if new_status == 'paid':
            total_paid = invoice.payments.aggregate(total=Sum('amount'))['total'] or 0
            if total_paid < invoice.total_amount:
                return Response({
                    'error': 'Cannot mark as paid. Payments do not cover the full amount.',
                    'total_paid': total_paid,
                    'total_amount': invoice.total_amount,
                    'balance': invoice.total_amount - total_paid
                }, status=status.HTTP_400_BAD_REQUEST)
        
        invoice.status = new_status
        
        if 'sent_via' in serializer.validated_data:
            invoice.sent_via = serializer.validated_data['sent_via']
            if not invoice.sent_date:
                invoice.sent_date = timezone.now()
        
        invoice.save()
        
        invoice_serializer = InvoiceSerializer(invoice)
        return Response(invoice_serializer.data)
    
    @action(detail=True, methods=['patch'], url_path='send')
    def send_invoice(self, request, pk=None):
        """
        Mark invoice as sent.
        PATCH /api/invoices/{id}/send/
        {
            "sent_via": "email" | "whatsapp"
        }
        """
        invoice = self.get_object()
        sent_via = request.data.get('sent_via', 'email')
        
        invoice.sent_date = timezone.now()
        invoice.sent_via = sent_via
        
        if invoice.status == 'draft':
            invoice.status = 'sent'
        
        invoice.save()
        
        invoice_serializer = InvoiceSerializer(invoice)
        return Response(invoice_serializer.data)
    
    @action(detail=True, methods=['post'], url_path='add-payment')
    def add_payment(self, request, pk=None):
        """
        Add a payment to an invoice.
        POST /api/invoices/{id}/add-payment/
        {
            "amount": 1000.00,
            "method": "bank_transfer",
            "reference": "BNK-12345",
            "payment_date": "2024-07-22",
            "notes": "Payment received"
        }
        """
        invoice = self.get_object()
        
        # Add invoice to request data
        data = request.data.copy()
        data['invoice'] = invoice.id
        
        serializer = PaymentCreateSerializer(data=data, context={'request': request})
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payment = serializer.save()
        
        # Update invoice amount paid
        total_paid = invoice.payments.aggregate(total=Sum('amount'))['total'] or 0
        invoice.amount_paid = total_paid
        
        if total_paid >= invoice.total_amount:
            invoice.status = 'paid'
        else:
            invoice.status = 'partially_paid'
        
        invoice.save()
        
        invoice_serializer = InvoiceSerializer(invoice)
        return Response(invoice_serializer.data)
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Get invoice statistics.
        GET /api/invoices/stats/
        """
        queryset = self.get_queryset()
        
        total = queryset.count()
        
        status_counts = {}
        for status_choice in Invoice.STATUS_CHOICES:
            status_code = status_choice[0]
            count = queryset.filter(status=status_code).count()
            if count > 0:
                status_counts[status_code] = count
        
        total_amount = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = queryset.aggregate(total=Sum('amount_paid'))['total'] or 0
        total_due = total_amount - total_paid
        
        overdue = queryset.filter(
            status__in=['sent', 'partially_paid'],
            due_date__lt=timezone.now().date()
        ).count()
        
        return Response({
            'total': total,
            'by_status': status_counts,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_due': total_due,
            'overdue': overdue
        })
        
    def destroy(self, request, *args, **kwargs):
        """Soft delete - cancel invoice"""
        invoice = self.get_object()
        
        # Check if invoice has payments
        if invoice.payments.exists():
            return Response({
                'error': 'Cannot delete an invoice with payments. Void the payments first.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if invoice.status == 'paid':
            return Response({
                'error': 'Cannot delete a paid invoice.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        invoice.status = 'cancelled'
        invoice.save()
        
        return Response({
            'message': f'Invoice {invoice.id} has been cancelled.',
            'invoice': InvoiceSerializer(invoice).data
        }, status=status.HTTP_200_OK)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    Payment ViewSet with CRUD operations.
    
    Provides:
    - list: GET /api/payments/
    - create: POST /api/payments/
    - retrieve: GET /api/payments/{id}/
    - update: PUT /api/payments/{id}/
    - partial_update: PATCH /api/payments/{id}/
    - destroy: DELETE /api/payments/{id}/
    """
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.select_related('invoice', 'created_by').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        else:
            return PaymentSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by invoice
        invoice = self.request.query_params.get('invoice')
        if invoice:
            queryset = queryset.filter(invoice_id=invoice)
        
        # Filter by method
        method = self.request.query_params.get('method')
        if method:
            queryset = queryset.filter(method=method)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(payment_date__gte=date_from)
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(payment_date__lte=date_to)
        
        return queryset.order_by('-payment_date')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """Delete payment and update invoice status"""
        payment = self.get_object()
        invoice = payment.invoice
        
        # Delete payment
        payment.delete()
        
        # Update invoice status
        total_paid = invoice.payments.aggregate(total=Sum('amount'))['total'] or 0
        invoice.amount_paid = total_paid
        
        if total_paid >= invoice.total_amount:
            invoice.status = 'paid'
        elif total_paid > 0:
            invoice.status = 'partially_paid'
        else:
            invoice.status = 'sent'
        
        invoice.save()
        
        return Response({
            'message': 'Payment deleted successfully.',
            'invoice': InvoiceSerializer(invoice).data
        }, status=status.HTTP_200_OK)