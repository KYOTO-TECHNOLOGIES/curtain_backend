from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import User, Role, AppPermission  # Removed Customer import

User = get_user_model()


class AppPermissionModelTest(TestCase):
    def setUp(self):
        self.permission = AppPermission.objects.create(
            name='can_view_appointments',
            description='Can view appointments'
        )
    
    def test_permission_creation(self):
        self.assertEqual(self.permission.name, 'can_view_appointments')
        self.assertTrue(self.permission.is_active)


class RoleModelTest(TestCase):
    def setUp(self):
        self.permission = AppPermission.objects.create(name='can_view_appointments')
        self.role = Role.objects.create(name='Admin')
        self.role.permissions.add(self.permission)
    
    def test_role_creation(self):
        self.assertEqual(self.role.name, 'Admin')
        self.assertEqual(self.role.permissions.count(), 1)