from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Users API (auth, users, roles, permissions)
    path('api/', include('users.urls')),

    # Customers API
    path('api/customers/', include('customers.urls')),

    # Appointments API
    path('api/appointments/', include('appointments.urls')),

    # Catalog API
    path('api/catalog/', include('catalog.urls')),

    # Activities API
    path('api/activities/', include('activities.urls')),
    
    # Quotations API
    path('api/quotations/', include('quotations.urls')),

    # Orders API
    path('api/', include('orders.urls')),

    # Inventory API
    path('api/inventory/', include('inventory.urls')),
]