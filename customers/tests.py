from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.db.models import Q
from users.models import Role, User
from .models import Customer

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


class CustomerAPITestCase(APITestCase, TestHelperMixin):
    """Test cases for Customer API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.admin = self.create_user(
            email='admin@example.com',
            password='adminpass123',
            role_name='Admin',
            full_name='Admin User',
            is_staff=True,
            is_superuser=True
        )
        
        self.customer_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+971501234567',
            'email': 'john.doe@example.com',
            'address_line_1': '123 Main St',
            'address_line_2': 'Apt 4B',
            'city': 'Dubai',
            'state': 'Dubai',
            'postal_code': '12345',
            'country': 'UAE',
            'notes': 'Test customer'
        }
        
        self.customer = Customer.objects.create(
            **self.customer_data,
            created_by=self.admin
        )
    
    def authenticate_admin(self):
        self.client.force_authenticate(user=self.admin)
    
    def test_list_customers(self):
        """Test retrieving list of customers"""
        self.authenticate_admin()
        url = reverse('customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The response is a list, not a paginated object
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'John')
    
    def test_create_customer(self):
        """Test creating a new customer"""
        self.authenticate_admin()
        url = reverse('customer-list')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '+9715087654321',
            'email': 'jane.smith@example.com',
            'address_line_1': '456 Park Ave',
            'city': 'Abu Dhabi',
            'country': 'UAE'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Jane')
        self.assertEqual(Customer.objects.count(), 2)
    
    def test_create_customer_duplicate_phone(self):
        """Test creating customer with existing phone number"""
        self.authenticate_admin()
        url = reverse('customer-list')
        data = {
            'first_name': 'John',
            'last_name': 'Doe Jr',
            'phone': '+971501234567',
            'email': 'john.jr@example.com'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone', response.data)
    
    def test_retrieve_customer(self):
        """Test retrieving single customer"""
        self.authenticate_admin()
        url = reverse('customer-detail', kwargs={'pk': self.customer.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['email'], 'john.doe@example.com')
    
    def test_update_customer(self):
        """Test updating customer"""
        self.authenticate_admin()
        url = reverse('customer-detail', kwargs={'pk': self.customer.id})
        data = {
            'first_name': 'Jonathan',
            'last_name': 'Doe',
            'phone': '+971501234567',
            'email': 'jonathan.doe@example.com'
        }
        
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Jonathan')
        
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'Jonathan')
    
    def test_search_customers(self):
        """Test searching customers by name or phone"""
        self.authenticate_admin()
        # Create more customers
        Customer.objects.create(
            first_name='Alice',
            last_name='Wonder',
            phone='+9715077777777',
            email='alice@example.com',
            created_by=self.admin
        )
        
        Customer.objects.create(
            first_name='Bob',
            last_name='Builder',
            phone='+9715088888888',
            email='bob@example.com',
            created_by=self.admin
        )
        
        url = reverse('customer-list')
        
        # Search by first name
        response = self.client.get(url, {'search': 'John'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'John')
        
        # Search by last name
        response = self.client.get(url, {'search': 'Wonder'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['first_name'], 'Alice')