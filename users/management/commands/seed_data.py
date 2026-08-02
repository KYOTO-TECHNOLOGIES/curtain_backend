from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import Role, AppPermission

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial data for the application'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Seeding initial data...'))
        
        # Create permissions
        permissions = [
            ('view_customers', 'Can view customers'),
            ('create_customers', 'Can create customers'),
            ('edit_customers', 'Can edit customers'),
            ('delete_customers', 'Can delete customers'),
            ('view_appointments', 'Can view appointments'),
            ('create_appointments', 'Can create appointments'),
            ('edit_appointments', 'Can edit appointments'),
            ('delete_appointments', 'Can delete appointments'),
            ('view_quotations', 'Can view quotations'),
            ('create_quotations', 'Can create quotations'),
            ('edit_quotations', 'Can edit quotations'),
            ('delete_quotations', 'Can delete quotations'),
            ('view_invoices', 'Can view invoices'),
            ('create_invoices', 'Can create invoices'),
            ('edit_invoices', 'Can edit invoices'),
            ('delete_invoices', 'Can delete invoices'),
        ]
        
        created_perms = []
        for perm_name, perm_desc in permissions:
            perm, created = AppPermission.objects.get_or_create(
                name=perm_name,
                defaults={'description': perm_desc}
            )
            if created:
                created_perms.append(perm_name)
        
        self.stdout.write(f'✓ Created {len(created_perms)} new permissions')
        self.stdout.write(f'✓ Total permissions: {AppPermission.objects.count()}')
        
        # Create roles
        roles_data = {
            'Admin': {
                'description': 'Full system access with all permissions',
                'permissions': [p[0] for p in permissions]
            },
            'Salesman': {
                'description': 'Can manage appointments, customers, and quotations',
                'permissions': [
                    'view_customers', 'create_customers', 'edit_customers',
                    'view_appointments', 'create_appointments', 'edit_appointments',
                    'view_quotations', 'create_quotations', 'edit_quotations',
                ]
            },
            'Receptionist': {
                'description': 'Can create appointments and view customers',
                'permissions': [
                    'view_customers', 'create_customers',
                    'view_appointments', 'create_appointments', 'edit_appointments',
                ]
            },
            'Accountant': {
                'description': 'Can view financial data and invoices',
                'permissions': [
                    'view_customers',
                    'view_appointments',
                    'view_quotations',
                    'view_invoices', 'create_invoices', 'edit_invoices',
                ]
            },
            'Production Manager': {
                'description': 'Can manage production and view orders',
                'permissions': [
                    'view_customers',
                    'view_appointments', 'edit_appointments',
                    'view_quotations', 'edit_quotations',
                ]
            }
        }
        
        created_roles = []
        for role_name, role_data in roles_data.items():
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={'description': role_data['description']}
            )
            if created:
                created_roles.append(role_name)
            
            # Add permissions to role
            for perm_name in role_data['permissions']:
                try:
                    perm = AppPermission.objects.get(name=perm_name)
                    role.permissions.add(perm)
                except AppPermission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'  ⚠ Permission "{perm_name}" not found'))
            
            self.stdout.write(f'  ✓ Role "{role_name}" has {role.permissions.count()} permissions')
        
        if created_roles:
            self.stdout.write(f'✓ Created {len(created_roles)} new roles')
        else:
            self.stdout.write('✓ All roles already exist')
        
        # Create admin user
        admin_role = Role.objects.get(name='Admin')
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'full_name': 'System Admin',
                'is_staff': True,
                'is_superuser': True,
                'role': admin_role
            }
        )
        
        if created:
            admin_user.set_password('adminpass123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created admin user: admin@example.com (password: adminpass123)'))
        else:
            # Update admin role if needed
            if admin_user.role != admin_role:
                admin_user.role = admin_role
                admin_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Admin user already exists: admin@example.com'))
        
        # Create sample salesman user
        salesman_role = Role.objects.get(name='Salesman')
        salesman, created = User.objects.get_or_create(
            email='salesman@example.com',
            defaults={
                'full_name': 'James Sales',
                'is_staff': False,
                'is_superuser': False,
                'role': salesman_role
            }
        )
        
        if created:
            salesman.set_password('salesmanpass123')
            salesman.save()
            self.stdout.write(self.style.SUCCESS('✓ Created salesman user: salesman@example.com (password: salesmanpass123)'))
        else:
            self.stdout.write('✓ Salesman user already exists')
        
        # Create sample receptionist user
        receptionist_role = Role.objects.get(name='Receptionist')
        receptionist, created = User.objects.get_or_create(
            email='receptionist@example.com',
            defaults={
                'full_name': 'Sarah Reception',
                'is_staff': False,
                'is_superuser': False,
                'role': receptionist_role
            }
        )
        
        if created:
            receptionist.set_password('receptionpass123')
            receptionist.save()
            self.stdout.write(self.style.SUCCESS('✓ Created receptionist user: receptionist@example.com (password: receptionpass123)'))
        else:
            self.stdout.write('✓ Receptionist user already exists')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Seeding complete!'))
        self.stdout.write(self.style.WARNING('\n📝 Login credentials:'))
        self.stdout.write('  Admin: admin@example.com / adminpass123')
        self.stdout.write('  Salesman: salesman@example.com / salesmanpass123')
        self.stdout.write('  Receptionist: receptionist@example.com / receptionpass123')