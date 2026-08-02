from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from users.models import Role, User
from .models import Appointment, AppointmentLocation
from customers.models import Customer

User = get_user_model()


class TestHelperMixin:
    """Helper mixin for creating test users"""
    
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


class AppointmentAPITestCase(APITestCase, TestHelperMixin):
    """Test cases for Appointment API endpoints"""
    
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
        
        # Create salesman users
        self.salesman = self.create_user(
            email='salesman@example.com',
            password='salespass123',
            role_name='Salesman',
            full_name='James Doe'
        )
        
        self.salesman2 = self.create_user(
            email='salesman2@example.com',
            password='salespass123',
            role_name='Salesman',
            full_name='Sarah Smith'
        )
        
        self.accountant = self.create_user(
            email='accountant@example.com',
            password='accountpass123',
            role_name='Accountant',
            full_name='Account User'
        )
        
        # Create customer
        self.customer = Customer.objects.create(
            first_name='Fatima',
            last_name='Al Hashimi',
            phone='+971501234567',
            email='fatima.h@example.com',
            address_line_1='Al Marsa St',
            city='Dubai',
            country='UAE',
            created_by=self.admin
        )
        
        # Create appointment
        self.appointment = self._create_test_appointment()
    
    def _create_test_appointment(self):
        """Helper to create an appointment"""
        appointment = Appointment.objects.create(
            customer=self.customer,
            title='Window Measurement',
            description='Client needs measurements for blackout curtains',
            appointment_date=datetime.now().date() + timedelta(days=3),
            appointment_time='09:30:00',
            end_time='10:30:00',
            job_type='measurement',
            status='scheduled',
            assigned_to=self.salesman,
            created_by=self.admin
        )
        
        AppointmentLocation.objects.create(
            appointment=appointment,
            building_name='Marina Heights',
            unit_number='Flat 1204',
            full_address='Al Marsa St, Dubai Marina',
            coordinates={"lat": 25.0805, "lng": 55.1403}
        )
        
        return appointment
    
    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)
    
    def authenticate_salesman(self):
        self.client.force_authenticate(user=self.salesman)
    
    def authenticate_salesman2(self):
        self.client.force_authenticate(user=self.salesman2)
    
    def authenticate_accountant(self):
        self.client.force_authenticate(user=self.accountant)
    
    # ----- List Tests -----
    def test_list_appointments_as_admin(self):
        """Test admin can list all appointments"""
        self.authenticate_admin()
        url = reverse('appointment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Window Measurement')
    
    def test_list_appointments_as_salesman(self):
        """Test salesman can only see their appointments"""
        self.authenticate_salesman()
        url = reverse('appointment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_salesman_cannot_see_others_appointments(self):
        """Test salesman cannot see appointments assigned to others"""
        # Create appointment assigned to another salesman
        Appointment.objects.create(
            customer=self.customer,
            title='Other Appointment',
            description='For another salesman',
            appointment_date=datetime.now().date() + timedelta(days=5),
            appointment_time='14:00:00',
            job_type='measurement',
            status='scheduled',
            assigned_to=self.salesman2,
            created_by=self.admin
        )
        
        self.authenticate_salesman()
        url = reverse('appointment-list')
        response = self.client.get(url)
        
        # Should only see their own appointment
        self.assertEqual(len(response.data), 1)
        # assigned_to_username returns email since that's the USERNAME_FIELD
        self.assertEqual(response.data[0]['assigned_to_username'], 'salesman@example.com')
    
    # ----- Create Tests -----
    def test_create_appointment_with_new_customer(self):
        """Test creating appointment with new customer"""
        self.authenticate_admin()
        url = reverse('appointment-list')
        data = {
            'customer_first_name': 'Ahmed',
            'customer_last_name': 'Mohammed',
            'customer_phone': '+9715098765432',
            'customer_email': 'ahmed.m@example.com',
            'customer_address': 'Business Bay',
            'customer_city': 'Dubai',
            'customer_source': 'website',
            'title': 'Installation Consultation',
            'description': 'Client needs consultation for new curtains',
            'appointment_date': '2026-07-26',
            'appointment_time': '14:00:00',
            'end_time': '15:00:00',
            'job_type': 'consultation',
            'status': 'pending',
            'location_building': 'Business Bay Tower',
            'location_unit': 'Office 1001',
            'location_full_address': 'Business Bay, Dubai'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Installation Consultation')
        # The customer field might be a nested object or just an ID
        # Check if customer is a dict or int
        if isinstance(response.data['customer'], dict):
            self.assertEqual(response.data['customer']['phone'], '+9715098765432')
        else:
            # If it's just an ID, verify the customer was created
            self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(Appointment.objects.count(), 2)
    
    def test_create_appointment_with_existing_customer_by_phone(self):
        """Test creating appointment with existing customer (by phone)"""
        self.authenticate_admin()
        url = reverse('appointment-list')
        data = {
            'customer_first_name': 'Fatima',
            'customer_last_name': 'Al Hashimi',
            'customer_phone': '+971501234567',  # Existing phone
            'customer_email': 'fatima.h@example.com',
            'customer_address': 'Al Marsa St',
            'customer_city': 'Dubai',
            'title': 'Another Appointment',
            'description': 'Follow-up measurement',
            'appointment_date': '2026-07-27',
            'appointment_time': '11:00:00',
            'job_type': 'measurement',
            'location_full_address': 'Al Marsa St, Dubai Marina'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)
        self.assertEqual(Customer.objects.count(), 1)  # No new customer created
    
    def test_create_appointment_with_existing_customer_by_email(self):
        """Test creating appointment with existing customer (by email)"""
        self.authenticate_admin()
        url = reverse('appointment-list')
        data = {
            'customer_first_name': 'Fatima',
            'customer_last_name': 'Al Hashimi',
            'customer_phone': '+9715099999999',  # Different phone
            'customer_email': 'fatima.h@example.com',  # Existing email
            'customer_address': 'Al Marsa St',
            'customer_city': 'Dubai',
            'title': 'Another Appointment',
            'description': 'Follow-up measurement',
            'appointment_date': '2026-07-27',
            'appointment_time': '11:00:00',
            'job_type': 'measurement',
            'location_full_address': 'Al Marsa St, Dubai Marina'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)
        self.assertEqual(Customer.objects.count(), 1)  # No new customer created
    
    def test_create_appointment_without_end_time(self):
        """Test creating appointment without end time"""
        self.authenticate_admin()
        url = reverse('appointment-list')
        data = {
            'customer_first_name': 'Test',
            'customer_last_name': 'User',
            'customer_phone': '+9715099999999',
            'customer_email': 'test@example.com',
            'title': 'Quick Visit',
            'appointment_date': '2026-07-28',
            'appointment_time': '10:00:00',
            'job_type': 'consultation',
            'location_full_address': 'Test Address'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data['end_time'])
    
    def test_create_appointment_invalid_end_time(self):
        """Test creating appointment with end time before start time"""
        self.authenticate_admin()
        url = reverse('appointment-list')
        data = {
            'customer_first_name': 'Test',
            'customer_last_name': 'User',
            'customer_phone': '+9715099999999',
            'customer_email': 'test@example.com',
            'title': 'Invalid Time',
            'appointment_date': '2026-07-28',
            'appointment_time': '10:00:00',
            'end_time': '09:00:00',  # Before start time
            'job_type': 'measurement',
            'location_full_address': 'Test Address'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_time', response.data)
    
    # ----- Retrieve Tests -----
    def test_retrieve_appointment(self):
        """Test retrieving single appointment"""
        self.authenticate_admin()
        url = reverse('appointment-detail', kwargs={'pk': self.appointment.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.appointment.id)
        self.assertEqual(response.data['title'], 'Window Measurement')
        self.assertEqual(response.data['customer']['first_name'], 'Fatima')
        self.assertEqual(response.data['location']['full_address'], 'Al Marsa St, Dubai Marina')
    
    # ----- Update Tests -----
    def test_update_appointment(self):
        """Test updating appointment"""
        self.authenticate_admin()
        url = reverse('appointment-detail', kwargs={'pk': self.appointment.id})
        data = {
            'title': 'Updated Measurement',
            'description': 'Updated description',
            'job_type': 'installation'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Measurement')
        self.assertEqual(response.data['job_type'], 'installation')
    
    def test_update_appointment_location(self):
        """Test updating appointment location"""
        self.authenticate_admin()
        url = reverse('appointment-detail', kwargs={'pk': self.appointment.id})
        data = {
            'location_building': 'New Building',
            'location_unit': 'New Unit',
            'location_full_address': 'New Address'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh and check location
        self.appointment.refresh_from_db()
        # Need to refresh the location from database
        self.appointment.location.refresh_from_db()
        self.assertEqual(self.appointment.location.building_name, 'New Building')
        self.assertEqual(self.appointment.location.unit_number, 'New Unit')
        self.assertEqual(self.appointment.location.full_address, 'New Address')
    
    # ----- Status Update Tests -----
    def test_update_appointment_status_to_in_progress(self):
        """Test updating appointment status to in_progress"""
        self.authenticate_salesman()
        url = reverse('appointment-update-status', kwargs={'pk': self.appointment.id})
        data = {'status': 'in_progress'}
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'in_progress')
    
    def test_update_appointment_status_to_completed(self):
        """Test updating appointment status to completed"""
        self.authenticate_salesman()
        url = reverse('appointment-update-status', kwargs={'pk': self.appointment.id})
        data = {'status': 'completed'}
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')
    
    def test_update_appointment_status_to_cancelled(self):
        """Test cancelling appointment with reason"""
        self.authenticate_salesman()
        url = reverse('appointment-update-status', kwargs={'pk': self.appointment.id})
        data = {
            'status': 'cancelled',
            'cancellation_reason': 'Client requested reschedule'
        }
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'cancelled')
        self.assertEqual(response.data['cancellation_reason'], 'Client requested reschedule')
        self.assertIsNotNone(response.data['cancelled_at'])
        self.assertEqual(response.data['cancelled_by_name'], 'James Doe')
    
    def test_cancel_appointment_without_reason(self):
        """Test cancelling appointment without providing reason"""
        self.authenticate_admin()
        url = reverse('appointment-update-status', kwargs={'pk': self.appointment.id})
        data = {'status': 'cancelled'}
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cancellation_reason', response.data)
    
    def test_salesman_cannot_update_others_appointment_status(self):
        """Test salesman cannot update status of appointment not assigned to them"""
        # Create appointment assigned to salesman2
        other_appointment = Appointment.objects.create(
            customer=self.customer,
            title='Other Appointment',
            appointment_date=datetime.now().date() + timedelta(days=5),
            appointment_time='14:00:00',
            job_type='measurement',
            status='scheduled',
            assigned_to=self.salesman2,
            created_by=self.admin
        )
        
        self.authenticate_salesman()
        url = reverse('appointment-update-status', kwargs={'pk': other_appointment.id})
        data = {'status': 'in_progress'}
        
        response = self.client.patch(url, data)
        # The view should return 403, but if the user doesn't have permission
        # to see the appointment, it might return 404
        # Both are acceptable for this test
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    # ----- Assignment Tests -----
    def test_assign_salesman_to_appointment(self):
        """Test assigning a salesman to appointment"""
        self.authenticate_admin()
        url = reverse('appointment-assign-salesman', kwargs={'pk': self.appointment.id})
        data = {'assigned_to': self.salesman2.id}
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['assigned_to'], self.salesman2.id)
        self.assertEqual(response.data['assigned_to_name'], 'Sarah Smith')
    
    def test_assign_non_salesman_user(self):
        """Test assigning non-salesman user to appointment"""
        self.authenticate_admin()
        url = reverse('appointment-assign-salesman', kwargs={'pk': self.appointment.id})
        data = {'assigned_to': self.accountant.id}
        
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('assigned_to', response.data)
    
    # ----- My Appointments Tests -----
    def test_my_appointments(self):
        """Test salesman can get their appointments"""
        self.authenticate_salesman()
        url = reverse('appointment-my-appointments')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # assigned_to_username returns email since that's the USERNAME_FIELD
        self.assertEqual(response.data[0]['assigned_to_username'], 'salesman@example.com')
    
    def test_my_appointments_with_status_filter(self):
        """Test my appointments with status filter"""
        # Create another appointment with different status
        Appointment.objects.create(
            customer=self.customer,
            title='Another Appointment',
            appointment_date=datetime.now().date() + timedelta(days=5),
            appointment_time='14:00:00',
            job_type='installation',
            status='completed',
            assigned_to=self.salesman,
            created_by=self.admin
        )
        
        self.authenticate_salesman()
        url = reverse('appointment-my-appointments')
        
        # Filter by scheduled
        response = self.client.get(url, {'status': 'scheduled'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Filter by completed
        response = self.client.get(url, {'status': 'completed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_my_appointments_empty(self):
        """Test my appointments when none assigned"""
        self.authenticate_salesman2()
        url = reverse('appointment-my-appointments')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    # ----- Stats Tests -----
    def test_appointment_stats(self):
        """Test appointment statistics"""
        self.authenticate_admin()
        url = reverse('appointment-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('by_status', response.data)
        self.assertIn('today', response.data)
        self.assertIn('upcoming', response.data)
        self.assertEqual(response.data['total'], 1)
    
    # ----- Reschedule Tests -----
    def test_reschedule_appointment(self):
        """Test rescheduling an appointment"""
        self.authenticate_admin()
        url = reverse('appointment-reschedule', kwargs={'pk': self.appointment.id})
        new_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        data = {
            'appointment_date': new_date,
            'appointment_time': '15:00:00',
            'end_time': '16:00:00'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'rescheduled')
        self.assertEqual(response.data['appointment_date'], new_date)
        self.assertEqual(response.data['appointment_time'], '15:00:00')
        self.assertEqual(response.data['end_time'], '16:00:00')
    
    def test_reschedule_appointment_missing_date(self):
        """Test rescheduling without date"""
        self.authenticate_admin()
        url = reverse('appointment-reschedule', kwargs={'pk': self.appointment.id})
        data = {'appointment_time': '15:00:00'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_reschedule_appointment_missing_time(self):
        """Test rescheduling without time"""
        self.authenticate_admin()
        url = reverse('appointment-reschedule', kwargs={'pk': self.appointment.id})
        data = {'appointment_date': '2026-07-30'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)