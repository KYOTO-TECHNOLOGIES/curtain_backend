from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from users.models import Role, User
from customers.models import Customer
from appointments.models import Appointment, AppointmentLocation
from catalog.models import WorkType, FabricType, Model as CatalogModel, CatalogItem, MotorType
from quotations.models import Quotation, QuotationArea, QuotationSurface, SurfaceSpec
from .models import Order, Invoice, Payment

User = get_user_model()


class TestHelperMixin:
    """Helper mixin for creating test data"""
    
    def create_role(self, name):
        role, _ = Role.objects.get_or_create(name=name)
        return role
    
    def create_user(self, email, password='testpass123', role_name=None, **kwargs):
        role = self.create_role(role_name) if role_name else None
        return User.objects.create_user(
            email=email,
            password=password,
            role=role,
            **kwargs
        )
    
    def create_customer(self, **kwargs):
        defaults = {
            'first_name': 'Test',
            'last_name': 'Customer',
            'phone': '+971501234567',
            'email': 'test.customer@example.com',
        }
        defaults.update(kwargs)
        return Customer.objects.create(**defaults)
    
    def create_appointment(self, customer=None, **kwargs):
        if not customer:
            customer = self.create_customer()
        
        defaults = {
            'customer': customer,
            'title': 'Test Appointment',
            'description': 'Test description',
            'appointment_date': timezone.now().date() + timedelta(days=3),
            'appointment_time': '10:00:00',
            'end_time': '11:00:00',
            'job_type': 'measurement',
            'status': 'scheduled',
        }
        defaults.update(kwargs)
        return Appointment.objects.create(**defaults)
    
    def create_work_type(self, **kwargs):
        defaults = {
            'name': 'Curtain&Blinds',
            'pricing_unit': 'm2',
            'features': {'motor': True, 'charges': True, 'images': True}
        }
        defaults.update(kwargs)
        work_type, _ = WorkType.objects.get_or_create(
            name=defaults['name'],
            defaults=defaults
        )
        return work_type
    
    def create_catalog_data(self, work_type=None):
        """Create catalog data using get_or_create to avoid duplicates"""
        if not work_type:
            work_type = self.create_work_type()
        
        fabric_type, _ = FabricType.objects.get_or_create(
            work_type=work_type,
            name='Curtains'
        )
        
        model, _ = CatalogModel.objects.get_or_create(
            fabric_type=fabric_type,
            name='American'
        )
        
        catalog_item, _ = CatalogItem.objects.get_or_create(
            model=model,
            name='Blackout',
            defaults={'price_per_unit': 120.00}
        )
        
        motor_type, _ = MotorType.objects.get_or_create(
            name='American Battery Motor',
            defaults={'price_per_m2': 180.00}
        )
        
        return {
            'work_type': work_type,
            'fabric_type': fabric_type,
            'model': model,
            'catalog_item': catalog_item,
            'motor_type': motor_type
        }
    
    def format_decimal(self, value):
        """Format decimal to 2 decimal places"""
        if value is None:
            return Decimal('0.00')
        return Decimal(str(value)).quantize(Decimal('0.01'))
    
    def create_quotation(self, customer=None, appointment=None, work_type=None, **kwargs):
        if not customer:
            customer = self.create_customer()
        if not appointment:
            appointment = self.create_appointment(customer=customer)
        if not work_type:
            work_type = self.create_work_type()
        
        defaults = {
            'customer': customer,
            'appointment': appointment,
            'work_type': work_type,
            'status': 'accepted',
            'quote_type': 'b2c',
            'discount_percentage': 0,
            'valid_until': timezone.now().date() + timedelta(days=30),
            'prepared_by': self.admin if hasattr(self, 'admin') else None
        }
        defaults.update(kwargs)
        
        quotation = Quotation.objects.create(**defaults)
        
        # Create area
        area = QuotationArea.objects.create(
            quotation=quotation,
            area_type='Master Bedroom',
            display_name='Room of Test',
            sort_order=0
        )
        
        # Create surface
        surface = QuotationSurface.objects.create(
            area=area,
            surface_name='Window 01',
            surface_type='window_curtain_path',
            width_cm=240,
            height_cm=310,
            opening_direction='one_way',
            sort_order=0
        )
        
        # Create spec
        catalog = self.create_catalog_data(work_type)
        SurfaceSpec.objects.create(
            surface=surface,
            fabric_type=catalog['fabric_type'],
            model=catalog['model'],
            catalog_item=catalog['catalog_item'],
            fabric_code='TEST-001',
            unit_price_per_m2=120.00,
            motor_control_type='motorized',
            motor_type=catalog['motor_type'],
            motor_price_per_unit=180.00,
            smart_integration=True,
            alexa_quantity=1,
            alexa_unit_price=200.00,
            pelmet_enabled=True,
            pelmet_width_cm=240,
            pelmet_price_per_metre=90.00,
            addon_label='Customization',
            addon_amount=50.00
        )
        
        # Recalculate and format totals
        quotation.recalc_totals()
        
        # Format totals to 2 decimal places
        quotation.subtotal = self.format_decimal(quotation.subtotal)
        quotation.vat = self.format_decimal(quotation.vat)
        quotation.total = self.format_decimal(quotation.total)
        quotation.save(update_fields=['subtotal', 'vat', 'total'])
        
        return quotation
    
    def create_order(self, quotation=None, customer=None, **kwargs):
        if not quotation:
            quotation = self.create_quotation(customer=customer)
        if not customer:
            customer = quotation.customer
        
        defaults = {
            'quotation': quotation,
            'customer': customer,
            'order_status': 'pending_production',
            'estimated_production_days': 21
        }
        defaults.update(kwargs)
        
        return Order.objects.create(**defaults)
    
    def create_invoice(self, order=None, customer=None, **kwargs):
        if not order:
            order = self.create_order(customer=customer)
        if not customer:
            customer = order.customer
        
        total = self.format_decimal(order.quotation.total) if order.quotation else Decimal('1000.00')
        
        defaults = {
            'order': order,
            'customer': customer,
            'total_amount': total,
            'amount_paid': Decimal('0.00'),
            'due_date': timezone.now().date() + timedelta(days=14),
            'payment_terms': 'Full payment on invoice',
            'status': 'sent'
        }
        defaults.update(kwargs)
        
        return Invoice.objects.create(**defaults)
    
    def create_payment(self, invoice=None, **kwargs):
        if not invoice:
            invoice = self.create_invoice()
        
        defaults = {
            'invoice': invoice,
            'amount': Decimal('500.00'),
            'method': 'bank_transfer',
            'reference': 'BNK-12345',
            'payment_date': timezone.now().date(),
            'created_by': self.admin if hasattr(self, 'admin') else None
        }
        defaults.update(kwargs)
        
        return Payment.objects.create(**defaults)


class OrderAPITestCase(APITestCase, TestHelperMixin):
    """Test cases for Order API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin = self.create_user(
            email='admin@example.com',
            password='adminpass123',
            role_name='Admin',
            full_name='Admin User',
            is_staff=True,
            is_superuser=True
        )
        
        # Create customer
        self.customer = self.create_customer(
            first_name='Mariam',
            last_name='Al Mansouri',
            phone='+971501234567',
            email='mariam.m@example.com'
        )
        
        # Create quotation
        self.quotation = self.create_quotation(customer=self.customer)
        
        # Create order
        self.order = self.create_order(quotation=self.quotation)
    
    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)
    
    # ----- Order List Tests -----
    def test_list_orders(self):
        """Test listing orders"""
        self.authenticate_admin()
        url = reverse('order-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['quotation_id'], self.quotation.id)
    
    def test_list_orders_with_filters(self):
        """Test listing orders with filters"""
        self.authenticate_admin()
        url = reverse('order-list')
        
        # Filter by status
        response = self.client.get(url, {'status': 'pending_production'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by customer
        response = self.client.get(url, {'customer': self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    # ----- Order Create Tests -----
    def test_create_order(self):
        """Test creating an order"""
        self.authenticate_admin()
        url = reverse('order-list')
        
        # Create new accepted quotation
        quotation = self.create_quotation(customer=self.customer)
        
        data = {
            'quotation': quotation.id,
            'customer': self.customer.id,
            'order_status': 'pending_production',
            'estimated_production_days': 21
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that the response has the expected fields
        # The create response uses OrderCreateSerializer which doesn't have quotation_id
        # Check the quotation field instead
        self.assertEqual(response.data['quotation'], quotation.id)
        self.assertEqual(response.data['order_status'], 'pending_production')
    
    def test_create_order_from_non_accepted_quotation(self):
        """Test creating order from non-accepted quotation"""
        self.authenticate_admin()
        url = reverse('order-list')
        
        # Create draft quotation
        quotation = self.create_quotation(customer=self.customer, status='draft')
        
        data = {
            'quotation': quotation.id,
            'customer': self.customer.id,
            'order_status': 'pending_production'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quotation', response.data)
    
    def test_create_duplicate_order(self):
        """Test creating order for quotation that already has an order"""
        self.authenticate_admin()
        url = reverse('order-list')
        
        data = {
            'quotation': self.quotation.id,
            'customer': self.customer.id,
            'order_status': 'pending_production'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quotation', response.data)
    
    # ----- Order Update Tests -----
    def test_update_order_status(self):
        """Test updating order status"""
        self.authenticate_admin()
        url = reverse('order-update-status', kwargs={'pk': self.order.id})
        
        data = {'order_status': 'in_production'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_status'], 'in_production')
    
    def test_update_order_status_to_closed(self):
        """Test updating order status to closed"""
        self.authenticate_admin()
        
        # Update through statuses
        self.order.order_status = 'in_production'
        self.order.save()
        
        url = reverse('order-update-status', kwargs={'pk': self.order.id})
        data = {'order_status': 'closed'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_status'], 'closed')
    
    # ----- Order Generate Invoice Tests -----
    def test_generate_invoice(self):
        """Test generating invoice from order"""
        self.authenticate_admin()
        url = reverse('order-generate-invoice', kwargs={'pk': self.order.id})
        
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            Decimal(response.data['total_amount']), 
            self.format_decimal(self.quotation.total)
        )
        self.assertEqual(response.data['customer'], self.customer.id)
        
        # Verify invoice was created
        self.order.refresh_from_db()
        self.assertTrue(hasattr(self.order, 'invoice'))
    
    def test_generate_invoice_already_exists(self):
        """Test generating invoice when one already exists"""
        self.authenticate_admin()
        
        # Create invoice first
        self.create_invoice(order=self.order)
        
        url = reverse('order-generate-invoice', kwargs={'pk': self.order.id})
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    # ----- Order Stats Tests -----
    def test_order_stats(self):
        """Test order statistics"""
        self.authenticate_admin()
        url = reverse('order-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('by_status', response.data)
        self.assertIn('pending_production', response.data)
        self.assertIn('in_production', response.data)
        self.assertEqual(response.data['total'], 1)
    
    # ----- Order Delete Tests -----
    def test_delete_order(self):
        """Test deleting/cancelling order"""
        self.authenticate_admin()
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_status, 'cancelled')
    
    def test_cannot_delete_closed_order(self):
        """Test cannot delete closed order"""
        self.authenticate_admin()
        
        self.order.order_status = 'closed'
        self.order.save()
        
        url = reverse('order-detail', kwargs={'pk': self.order.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    # ----- Order Permission Tests -----
    def test_unauthorized_access(self):
        """Test unauthenticated access"""
        self.client.force_authenticate(user=None)
        url = reverse('order-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class InvoiceAPITestCase(APITestCase, TestHelperMixin):
    """Test cases for Invoice API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin = self.create_user(
            email='admin@example.com',
            password='adminpass123',
            role_name='Admin',
            full_name='Admin User',
            is_staff=True,
            is_superuser=True
        )
        
        # Create customer
        self.customer = self.create_customer(
            first_name='Mariam',
            last_name='Al Mansouri',
            phone='+971501234567',
            email='mariam.m@example.com'
        )
        
        # Create quotation and order
        self.quotation = self.create_quotation(customer=self.customer)
        self.order = self.create_order(quotation=self.quotation)
        
        # Create invoice
        self.invoice = self.create_invoice(order=self.order)
    
    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)
    
    # ----- Invoice List Tests -----
    def test_list_invoices(self):
        """Test listing invoices"""
        self.authenticate_admin()
        url = reverse('invoice-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.invoice.id)
    
    def test_list_invoices_with_filters(self):
        """Test listing invoices with filters"""
        self.authenticate_admin()
        url = reverse('invoice-list')
        
        # Filter by status
        response = self.client.get(url, {'status': 'sent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by customer
        response = self.client.get(url, {'customer': self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    # ----- Invoice Create Tests -----
    def test_create_invoice(self):
        """Test creating an invoice"""
        self.authenticate_admin()
        url = reverse('invoice-list')
        
        # Create new order
        quotation = self.create_quotation(customer=self.customer)
        order = self.create_order(quotation=quotation)
        
        total = self.format_decimal(quotation.total)
        
        data = {
            'order': order.id,
            'customer': self.customer.id,
            'total_amount': str(total),
            'due_date': (timezone.now().date() + timedelta(days=14)).isoformat(),
            'payment_terms': 'Full payment on invoice'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['order'], order.id)
        self.assertEqual(
            Decimal(response.data['total_amount']), 
            total
        )
    
    def test_create_invoice_duplicate(self):
        """Test creating invoice when one already exists"""
        self.authenticate_admin()
        url = reverse('invoice-list')
        
        data = {
            'order': self.order.id,
            'customer': self.customer.id,
            'total_amount': '1000.00',
            'due_date': (timezone.now().date() + timedelta(days=14)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('order', response.data)
    
    # ----- Invoice Update Tests -----
    def test_update_invoice_status_to_paid(self):
        """Test updating invoice status to paid"""
        self.authenticate_admin()
        
        # Add payment first
        total = self.format_decimal(self.invoice.total_amount)
        self.create_payment(invoice=self.invoice, amount=total)
        
        url = reverse('invoice-update-status', kwargs={'pk': self.invoice.id})
        data = {'status': 'paid'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'paid')
    
    def test_update_invoice_status_to_paid_without_payment(self):
        """Test updating invoice to paid without payment"""
        self.authenticate_admin()
        url = reverse('invoice-update-status', kwargs={'pk': self.invoice.id})
        data = {'status': 'paid'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_send_invoice(self):
        """Test sending invoice"""
        self.authenticate_admin()
        url = reverse('invoice-send-invoice', kwargs={'pk': self.invoice.id})
        data = {'sent_via': 'whatsapp'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['sent_via'], 'whatsapp')
        self.assertIsNotNone(response.data['sent_date'])
        self.assertEqual(response.data['status'], 'sent')
    
    # ----- Invoice Payment Tests -----
    def test_add_payment_to_invoice(self):
        """Test adding payment to invoice"""
        self.authenticate_admin()
        url = reverse('invoice-add-payment', kwargs={'pk': self.invoice.id})
        
        data = {
            'amount': '500.00',
            'method': 'bank_transfer',
            'reference': 'BNK-12345',
            'payment_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'partially_paid')
        self.assertEqual(response.data['amount_paid'], '500.00')
        
        # Verify payment was created
        self.assertEqual(self.invoice.payments.count(), 1)
    
    def test_add_payment_full_amount(self):
        """Test adding full payment to invoice"""
        self.authenticate_admin()
        url = reverse('invoice-add-payment', kwargs={'pk': self.invoice.id})
        
        total = self.format_decimal(self.invoice.total_amount)
        
        data = {
            'amount': str(total),
            'method': 'bank_transfer',
            'reference': 'BNK-12345',
            'payment_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'paid')
    
    def test_add_payment_exceeds_balance(self):
        """Test adding payment that exceeds balance"""
        self.authenticate_admin()
        url = reverse('invoice-add-payment', kwargs={'pk': self.invoice.id})
        
        total = self.format_decimal(self.invoice.total_amount + 1000)
        
        data = {
            'amount': str(total),
            'method': 'bank_transfer',
            'reference': 'BNK-12345',
            'payment_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    # ----- Invoice Stats Tests -----
    def test_invoice_stats(self):
        """Test invoice statistics"""
        self.authenticate_admin()
        url = reverse('invoice-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('by_status', response.data)
        self.assertIn('total_amount', response.data)
        self.assertIn('total_paid', response.data)
        self.assertIn('total_due', response.data)
        self.assertIn('overdue', response.data)
    
    # ----- Invoice Delete Tests -----
    def test_delete_invoice(self):
        """Test deleting/cancelling invoice"""
        self.authenticate_admin()
        url = reverse('invoice-detail', kwargs={'pk': self.invoice.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'cancelled')
    
    def test_cannot_delete_invoice_with_payments(self):
        """Test cannot delete invoice with payments"""
        self.authenticate_admin()
        
        # Add payment
        self.create_payment(invoice=self.invoice, amount=Decimal('500.00'))
        
        url = reverse('invoice-detail', kwargs={'pk': self.invoice.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    # ----- Invoice Permission Tests -----
    def test_unauthorized_invoice_access(self):
        """Test unauthenticated access to invoices"""
        self.client.force_authenticate(user=None)
        url = reverse('invoice-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PaymentAPITestCase(APITestCase, TestHelperMixin):
    """Test cases for Payment API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin = self.create_user(
            email='admin@example.com',
            password='adminpass123',
            role_name='Admin',
            full_name='Admin User',
            is_staff=True,
            is_superuser=True
        )
        
        # Create customer
        self.customer = self.create_customer()
        
        # Create quotation, order, and invoice
        self.quotation = self.create_quotation(customer=self.customer)
        self.order = self.create_order(quotation=self.quotation)
        self.invoice = self.create_invoice(order=self.order)
        
        # Create payment
        self.payment = self.create_payment(invoice=self.invoice)
    
    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)
    
    # ----- Payment List Tests -----
    def test_list_payments(self):
        """Test listing payments"""
        self.authenticate_admin()
        url = reverse('payment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['invoice_number'], self.invoice.id)
    
    def test_list_payments_with_filters(self):
        """Test listing payments with filters"""
        self.authenticate_admin()
        url = reverse('payment-list')
        
        # Filter by invoice
        response = self.client.get(url, {'invoice': self.invoice.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by method
        response = self.client.get(url, {'method': 'bank_transfer'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    # ----- Payment Create Tests -----
    def test_create_payment(self):
        """Test creating a payment"""
        self.authenticate_admin()
        url = reverse('payment-list')
        
        data = {
            'invoice': self.invoice.id,
            'amount': '300.00',
            'method': 'cash',
            'reference': 'CASH-001',
            'payment_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['amount'], '300.00')
        self.assertEqual(response.data['method'], 'cash')
        
        # Verify invoice status updated
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'partially_paid')
    
    def test_create_payment_zero_amount(self):
        """Test creating payment with zero amount"""
        self.authenticate_admin()
        url = reverse('payment-list')
        
        data = {
            'invoice': self.invoice.id,
            'amount': '0.00',
            'method': 'cash',
            'payment_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('amount', response.data)
    
    # ----- Payment Delete Tests -----
    def test_delete_payment(self):
        """Test deleting payment"""
        self.authenticate_admin()
        url = reverse('payment-detail', kwargs={'pk': self.payment.id})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify invoice status updated
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'sent')
        self.assertEqual(self.invoice.amount_paid, Decimal('0.00'))
    
    # ----- Payment Permission Tests -----
    def test_unauthorized_payment_access(self):
        """Test unauthenticated access to payments"""
        self.client.force_authenticate(user=None)
        url = reverse('payment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderModelTest(TestCase, TestHelperMixin):
    """Test Order model methods"""
    
    def setUp(self):
        self.admin = self.create_user(
            email='admin@example.com',
            password='adminpass123',
            role_name='Admin'
        )
        self.customer = self.create_customer()
        self.quotation = self.create_quotation(customer=self.customer)
        self.order = self.create_order(quotation=self.quotation)
    
    def test_order_creation(self):
        """Test order creation"""
        self.assertEqual(self.order.quotation, self.quotation)
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.order.order_status, 'pending_production')
        self.assertEqual(self.order.estimated_production_days, 21)
    
    def test_order_str_method(self):
        """Test order string representation"""
        expected = f"Order for {self.quotation.id}"
        self.assertEqual(str(self.order), expected)


class InvoiceModelTest(TestCase, TestHelperMixin):
    """Test Invoice model methods"""
    
    def setUp(self):
        self.admin = self.create_user(
            email='admin@example.com',
            password='adminpass123',
            role_name='Admin'
        )
        self.customer = self.create_customer()
        self.quotation = self.create_quotation(customer=self.customer)
        self.order = self.create_order(quotation=self.quotation)
        self.invoice = self.create_invoice(order=self.order)
        
        # Format totals to 2 decimal places
        self.invoice.total_amount = self.format_decimal(self.invoice.total_amount)
        self.invoice.amount_paid = self.format_decimal(self.invoice.amount_paid)
        self.invoice.save()
    
    def test_invoice_creation(self):
        """Test invoice creation"""
        self.assertEqual(self.invoice.order, self.order)
        self.assertEqual(self.invoice.customer, self.customer)
        self.assertEqual(self.invoice.total_amount, self.quotation.total)
        self.assertEqual(self.invoice.status, 'sent')
    
    def test_invoice_str_method(self):
        """Test invoice string representation"""
        self.assertEqual(str(self.invoice), self.invoice.id)
    
    def test_invoice_balance_due(self):
        """Test invoice balance due calculation"""
        # Get total as Decimal with 2 decimal places
        total = self.format_decimal(self.invoice.total_amount)
        
        # Initial balance should equal total amount
        self.assertEqual(
            self.invoice.balance_due, 
            total
        )
        
        # Add payment with 2 decimal places
        payment_amount = Decimal('500.00')
        self.create_payment(invoice=self.invoice, amount=payment_amount)
        
        # Refresh invoice from database to get updated amount_paid
        self.invoice.refresh_from_db()
        
        # Calculate expected balance
        expected_balance = total - payment_amount
        
        # Verify balance due
        self.assertEqual(
            self.invoice.balance_due, 
            expected_balance
        )
        
        # Verify amount_paid was updated
        self.assertEqual(self.invoice.amount_paid, payment_amount)

class PaymentModelTest(TestCase, TestHelperMixin):
    """Test Payment model methods"""
    
    def setUp(self):
        self.admin = self.create_user(
            email='admin@example.com',
            password='adminpass123',
            role_name='Admin'
        )
        self.customer = self.create_customer()
        self.quotation = self.create_quotation(customer=self.customer)
        self.order = self.create_order(quotation=self.quotation)
        self.invoice = self.create_invoice(order=self.order)
        self.payment = self.create_payment(invoice=self.invoice)
    
    def test_payment_creation(self):
        """Test payment creation"""
        self.assertEqual(self.payment.invoice, self.invoice)
        self.assertEqual(self.payment.amount, Decimal('500.00'))
        self.assertEqual(self.payment.method, 'bank_transfer')
        self.assertEqual(self.payment.created_by, self.admin)
    
    def test_payment_str_method(self):
        """Test payment string representation"""
        expected = f"{self.invoice.id} - 500.00"
        self.assertEqual(str(self.payment), expected)