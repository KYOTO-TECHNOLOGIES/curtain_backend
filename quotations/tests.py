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
from .models import Quotation, QuotationArea, QuotationSurface, SurfaceSpec

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
        return WorkType.objects.create(**defaults)
    
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
            'status': 'draft',
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
        
        # Create spec if catalog data available
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
        
        # Recalculate totals
        quotation.recalc_totals()
        
        return quotation


class QuotationAPITestCase(APITestCase, TestHelperMixin):
    """Test cases for Quotation API endpoints"""
    
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
        
        # Create salesman user
        self.salesman = self.create_user(
            email='salesman@example.com',
            password='salespass123',
            role_name='Salesman',
            full_name='James Doe'
        )
        
        # Create customer
        self.customer = self.create_customer(
            first_name='Mariam',
            last_name='Al Mansouri',
            phone='+971501234567',
            email='mariam.m@example.com'
        )
        
        # Create appointment
        self.appointment = self.create_appointment(
            customer=self.customer,
            title='Window Measurement',
            appointment_date=timezone.now().date() + timedelta(days=3),
            appointment_time='09:30:00'
        )
        
        # Create work type and catalog data
        self.work_type = self.create_work_type()
        self.catalog = self.create_catalog_data(self.work_type)
        
        # Create quotation
        self.quotation = self.create_quotation(
            customer=self.customer,
            appointment=self.appointment,
            work_type=self.work_type
        )
    
    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)
    
    def authenticate_salesman(self):
        self.client.force_authenticate(user=self.salesman)
    
    # ----- List Tests -----
    def test_list_quotations_as_admin(self):
        """Test admin can list all quotations"""
        self.authenticate_admin()
        url = reverse('quotation-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.quotation.id)
    
    def test_list_quotations_with_filters(self):
        """Test listing quotations with filters"""
        self.authenticate_admin()
        url = reverse('quotation-list')
        
        # Filter by status
        response = self.client.get(url, {'status': 'draft'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by customer
        response = self.client.get(url, {'customer': self.customer.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by quote type
        response = self.client.get(url, {'quote_type': 'b2c'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_list_quotations_with_search(self):
        """Test searching quotations"""
        self.authenticate_admin()
        url = reverse('quotation-list')
        
        # Search by customer name
        response = self.client.get(url, {'search': 'Mariam'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Search by quotation ID
        response = self.client.get(url, {'search': self.quotation.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    # ----- Create Tests -----
    def test_create_quotation(self):
        """Test creating a new quotation"""
        self.authenticate_admin()
        url = reverse('quotation-list')
        
        catalog = self.create_catalog_data(self.work_type)
        
        data = {
            'customer': self.customer.id,
            'appointment': self.appointment.id,
            'work_type': self.work_type.id,
            'status': 'draft',
            'quote_type': 'b2c',
            'valid_until': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'discount_percentage': 0,
            'areas_data': [
                {
                    'area_type': 'Living Room',
                    'display_name': 'Room of Mariam',
                    'sort_order': 0,
                    'surfaces': [
                        {
                            'surface_name': 'Window 01',
                            'surface_type': 'window_curtain_path',
                            'width_cm': 240,
                            'height_cm': 310,
                            'opening_direction': 'one_way',
                            'special_requirements': 'Blackout required',
                            'sort_order': 0,
                            'spec': {
                                'fabric_type': catalog['fabric_type'].id,
                                'model': catalog['model'].id,
                                'catalog_item': catalog['catalog_item'].id,
                                'fabric_code': 'TEST-002',
                                'unit_price_per_m2': 120.00,
                                'motor_control_type': 'motorized',
                                'motor_type': catalog['motor_type'].id,
                                'motor_price_per_unit': 180.00,
                                'smart_integration': True,
                                'alexa_quantity': 1,
                                'alexa_unit_price': 200.00,
                                'pelmet_enabled': True,
                                'pelmet_width_cm': 240,
                                'pelmet_price_per_metre': 90.00,
                                'addon_label': 'Customization',
                                'addon_amount': 50.00
                            }
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'draft')
        self.assertEqual(response.data['customer'], self.customer.id)
        self.assertIn('areas', response.data)
        self.assertEqual(len(response.data['areas']), 1)
        self.assertEqual(len(response.data['areas'][0]['surfaces']), 1)
    
    def test_create_quotation_without_areas(self):
        """Test creating quotation without areas"""
        self.authenticate_admin()
        url = reverse('quotation-list')
        
        data = {
            'customer': self.customer.id,
            'appointment': self.appointment.id,
            'work_type': self.work_type.id,
            'status': 'draft',
            'quote_type': 'b2c',
            'valid_until': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'discount_percentage': 0,
            'areas_data': []
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('areas', response.data)
        self.assertEqual(len(response.data['areas']), 0)
    
    def test_create_quotation_invalid_discount(self):
        """Test creating quotation with invalid discount"""
        self.authenticate_admin()
        url = reverse('quotation-list')
        
        data = {
            'customer': self.customer.id,
            'appointment': self.appointment.id,
            'work_type': self.work_type.id,
            'status': 'draft',
            'quote_type': 'b2c',
            'valid_until': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'discount_percentage': 150,
            'areas_data': []
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('discount_percentage', response.data)
    
    # ----- Retrieve Tests -----
    def test_retrieve_quotation(self):
        """Test retrieving single quotation"""
        self.authenticate_admin()
        url = reverse('quotation-detail', kwargs={'pk': self.quotation.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.quotation.id)
        self.assertEqual(response.data['customer_name'], 'Mariam Al Mansouri')
        self.assertEqual(len(response.data['areas']), 1)
        self.assertEqual(len(response.data['areas'][0]['surfaces']), 1)
        self.assertIsNotNone(response.data['areas'][0]['surfaces'][0]['spec'])
    
    # ----- Update Tests -----
    def test_update_quotation(self):
        """Test updating quotation"""
        self.authenticate_admin()
        url = reverse('quotation-detail', kwargs={'pk': self.quotation.id})
        
        data = {
            'status': 'pending',
            'discount_percentage': 10
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'pending')
        self.assertEqual(response.data['discount_percentage'], '10.00')
        
        # Verify recalculated totals
        self.quotation.refresh_from_db()
        self.assertEqual(self.quotation.discount_percentage, Decimal('10.00'))
    
    def test_update_quotation_with_areas(self):
        """Test updating quotation with new areas"""
        self.authenticate_admin()
        url = reverse('quotation-detail', kwargs={'pk': self.quotation.id})
        
        catalog = self.create_catalog_data(self.work_type)
        
        data = {
            'status': 'draft',
            'areas_data': [
                {
                    'area_type': 'New Room',
                    'display_name': 'New Room Name',
                    'sort_order': 0,
                    'surfaces': [
                        {
                            'surface_name': 'New Window',
                            'surface_type': 'window_curtain_path',
                            'width_cm': 300,
                            'height_cm': 250,
                            'opening_direction': 'two_way',
                            'sort_order': 0,
                            'spec': {
                                'fabric_type': catalog['fabric_type'].id,
                                'model': catalog['model'].id,
                                'catalog_item': catalog['catalog_item'].id,
                                'fabric_code': 'NEW-001',
                                'unit_price_per_m2': 150.00,
                                'motor_control_type': 'manual',
                                'smart_integration': False,
                                'pelmet_enabled': False,
                                'pelmet_price_per_metre': 0,
                                'addon_amount': 0
                            }
                        }
                    ]
                }
            ]
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('areas', response.data)
        self.assertEqual(len(response.data['areas']), 1)
        self.assertEqual(response.data['areas'][0]['display_name'], 'New Room Name')
    
    # ----- Status Update Tests -----
    def test_update_status_to_sent(self):
        """Test updating quotation status to sent"""
        self.authenticate_admin()
        url = reverse('quotation-update-status', kwargs={'pk': self.quotation.id})
        
        data = {
            'status': 'sent',
            'sent_via': 'email'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'sent')
        self.assertIsNotNone(response.data['sent_date'])
        self.assertEqual(response.data['sent_via'], 'email')
    
    def test_update_status_to_accepted(self):
        """Test updating quotation status to accepted"""
        self.authenticate_admin()
        
        # First set to sent
        self.quotation.status = 'sent'
        self.quotation.save()
        
        url = reverse('quotation-update-status', kwargs={'pk': self.quotation.id})
        data = {'status': 'accepted'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'accepted')
        self.assertIsNotNone(response.data['accepted_date'])
    
    def test_update_status_to_cancelled(self):
        """Test updating quotation status to cancelled"""
        self.authenticate_admin()
        url = reverse('quotation-update-status', kwargs={'pk': self.quotation.id})
        
        data = {'status': 'cancelled'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')
    
    def test_cannot_update_accepted_status(self):
        """Test cannot update accepted quotation except to cancel"""
        self.authenticate_admin()
        
        # Set to accepted
        self.quotation.status = 'accepted'
        self.quotation.save()
        
        url = reverse('quotation-update-status', kwargs={'pk': self.quotation.id})
        data = {'status': 'draft'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_cannot_update_cancelled_status(self):
        """Test cannot update cancelled quotation"""
        self.authenticate_admin()
        
        # Set to cancelled
        self.quotation.status = 'cancelled'
        self.quotation.save()
        
        url = reverse('quotation-update-status', kwargs={'pk': self.quotation.id})
        data = {'status': 'draft'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    # ----- Custom Action Tests -----
    def test_send_quotation(self):
        """Test sending a quotation"""
        self.authenticate_admin()
        url = reverse('quotation-send-quotation', kwargs={'pk': self.quotation.id})
        
        data = {'sent_via': 'whatsapp'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'sent')
        self.assertEqual(response.data['sent_via'], 'whatsapp')
        self.assertIsNotNone(response.data['sent_date'])
    
    def test_accept_quotation(self):
        """Test accepting a quotation"""
        self.authenticate_admin()
        
        # First set to sent
        self.quotation.status = 'sent'
        self.quotation.save()
        
        url = reverse('quotation-accept-quotation', kwargs={'pk': self.quotation.id})
        response = self.client.patch(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'accepted')
        self.assertIsNotNone(response.data['accepted_date'])
    
    def test_cancel_quotation(self):
        """Test cancelling a quotation"""
        self.authenticate_admin()
        url = reverse('quotation-cancel-quotation', kwargs={'pk': self.quotation.id})
        
        data = {'cancellation_reason': 'Client changed mind'}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')
    
    def test_cannot_cancel_already_cancelled(self):
        """Test cannot cancel already cancelled quotation"""
        self.authenticate_admin()
        
        self.quotation.status = 'cancelled'
        self.quotation.save()
        
        url = reverse('quotation-cancel-quotation', kwargs={'pk': self.quotation.id})
        data = {'cancellation_reason': 'Try again'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    # ----- Duplicate Tests -----
    def test_duplicate_quotation(self):
        """Test duplicating a quotation"""
        self.authenticate_admin()
        url = reverse('quotation-duplicate', kwargs={'pk': self.quotation.id})
        
        response = self.client.post(url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data['id'], self.quotation.id)
        self.assertEqual(response.data['customer'], self.customer.id)
        self.assertEqual(response.data['work_type'], self.work_type.id)
        self.assertEqual(len(response.data['areas']), 1)
        self.assertEqual(len(response.data['areas'][0]['surfaces']), 1)
        
        # Check spec data copied
        spec = response.data['areas'][0]['surfaces'][0]['spec']
        self.assertEqual(spec['fabric_code'], 'TEST-001')
        self.assertEqual(spec['unit_price_per_m2'], '120.00')
    
    def test_duplicate_quotation_with_new_customer(self):
        """Test duplicating quotation with new customer"""
        self.authenticate_admin()
        
        new_customer = self.create_customer(
            first_name='New',
            last_name='Customer',
            phone='+9715099999999'
        )
        
        url = reverse('quotation-duplicate', kwargs={'pk': self.quotation.id})
        data = {'customer': new_customer.id}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['customer'], new_customer.id)
    
    # ----- Stats Tests -----
    def test_quotation_stats(self):
        """Test quotation statistics"""
        self.authenticate_admin()
        url = reverse('quotation-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('by_status', response.data)
        self.assertIn('total_value', response.data)
        self.assertIn('accepted_value', response.data)
        self.assertIn('pending_value', response.data)
        self.assertIn('this_month', response.data)
        
        self.assertEqual(response.data['total'], 1)
        self.assertIn('draft', response.data['by_status'])
    
    # ----- Delete Tests -----
    def test_delete_quotation(self):
        """Test deleting/cancelling quotation"""
        self.authenticate_admin()
        url = reverse('quotation-detail', kwargs={'pk': self.quotation.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify status changed to cancelled
        self.quotation.refresh_from_db()
        self.assertEqual(self.quotation.status, 'cancelled')
    
    def test_cannot_delete_accepted_quotation(self):
        """Test cannot delete accepted quotation"""
        self.authenticate_admin()
        
        self.quotation.status = 'accepted'
        self.quotation.save()
        
        url = reverse('quotation-detail', kwargs={'pk': self.quotation.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    # ----- Permission Tests -----
    def test_unauthorized_access(self):
        """Test unauthenticated access"""
        self.client.force_authenticate(user=None)
        url = reverse('quotation-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_salesman_can_view_quotations(self):
        """Test salesman can view quotations"""
        self.authenticate_salesman()
        url = reverse('quotation-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_salesman_can_create_quotation(self):
        """Test salesman can create quotation"""
        self.authenticate_salesman()
        url = reverse('quotation-list')
        
        data = {
            'customer': self.customer.id,
            'appointment': self.appointment.id,
            'work_type': self.work_type.id,
            'status': 'draft',
            'quote_type': 'b2c',
            'valid_until': (timezone.now().date() + timedelta(days=30)).isoformat(),
            'discount_percentage': 0,
            'areas_data': []
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class QuotationModelTest(TestCase, TestHelperMixin):
    """Test Quotation model methods"""
    
    def setUp(self):
        self.admin = self.create_user(
            email='admin@example.com',
            password='adminpass123',
            role_name='Admin'
        )
        self.customer = self.create_customer()
        self.work_type = self.create_work_type()
        self.appointment = self.create_appointment(customer=self.customer)
        self.catalog = self.create_catalog_data(self.work_type)
        
        self.quotation = Quotation.objects.create(
            customer=self.customer,
            appointment=self.appointment,
            work_type=self.work_type,
            prepared_by=self.admin,
            status='draft',
            quote_type='b2c',
            valid_until=timezone.now().date() + timedelta(days=30)
        )
        
        # Create area and surface with spec
        self.area = QuotationArea.objects.create(
            quotation=self.quotation,
            area_type='Living Room',
            display_name='Living Room'
        )
        
        self.surface = QuotationSurface.objects.create(
            area=self.area,
            surface_name='Window 01',
            surface_type='window_curtain_path',
            width_cm=240,
            height_cm=310
        )
        
        self.spec = SurfaceSpec.objects.create(
            surface=self.surface,
            fabric_type=self.catalog['fabric_type'],
            model=self.catalog['model'],
            catalog_item=self.catalog['catalog_item'],
            fabric_code='TEST-001',
            unit_price_per_m2=120.00,
            motor_control_type='motorized',
            motor_type=self.catalog['motor_type'],
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
    
    def test_quotation_id_generation(self):
        """Test automatic ID generation"""
        new_quotation = Quotation.objects.create(
            customer=self.customer,
            appointment=self.appointment,
            work_type=self.work_type,
            prepared_by=self.admin,
            status='draft',
            quote_type='b2c',
            valid_until=timezone.now().date() + timedelta(days=30)
        )
        self.assertTrue(new_quotation.id.startswith('QT-'))
    
    def test_quotation_recalc_totals(self):
        """Test total recalculation"""
        # Recalculate totals
        self.quotation.recalc_totals()
        
        # Calculate expected value based on model calculations
        area = (Decimal('240') / Decimal('100')) * (Decimal('310') / Decimal('100'))
        fabric_total = area * Decimal('120')
        motor_charge = area * Decimal('180')
        alexa_total = Decimal('1') * Decimal('200')
        pelmet_total = (Decimal('240') / Decimal('100')) * Decimal('90')
        addon = Decimal('50')
        
        expected = fabric_total + motor_charge + alexa_total + pelmet_total + addon
        
        self.assertEqual(self.quotation.subtotal, expected)
        self.assertEqual(self.quotation.vat, expected * Decimal('0.05'))
        self.assertEqual(self.quotation.total, expected + (expected * Decimal('0.05')))
    
    def test_quotation_status_choices(self):
        """Test status choices"""
        choices = [choice[0] for choice in Quotation.STATUS_CHOICES]
        self.assertIn('draft', choices)
        self.assertIn('pending', choices)
        self.assertIn('sent', choices)
        self.assertIn('accepted', choices)
        self.assertIn('cancelled', choices)
    
    def test_quotation_str_method(self):
        """Test string representation"""
        self.assertEqual(str(self.quotation), self.quotation.id)
    
    def test_area_str_method(self):
        """Test area string representation"""
        self.assertEqual(str(self.area), 'Living Room')
    
    def test_surface_str_method(self):
        """Test surface string representation"""
        expected = 'Living Room - Window 01'
        self.assertEqual(str(self.surface), expected)
    
    def test_spec_calculation(self):
        """Test spec auto-calculation"""
        self.spec.refresh_from_db()
        
        # Calculate expected value based on model calculations
        area = (Decimal('240') / Decimal('100')) * (Decimal('310') / Decimal('100'))
        fabric_total = area * Decimal('120')
        motor_charge = area * Decimal('180')
        alexa_total = Decimal('1') * Decimal('200')
        pelmet_total = (Decimal('240') / Decimal('100')) * Decimal('90')
        addon = Decimal('50')
        
        expected = fabric_total + motor_charge + alexa_total + pelmet_total + addon
        
        self.assertEqual(self.spec.line_item_total, expected)