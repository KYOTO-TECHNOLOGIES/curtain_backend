# from django.urls import path

# from .views import (
#     ChangePasswordView,
#     CustomerDetailView,
#     CustomerListCreateView,
#     LoginView,
#     LogoutView,
#     MeView,
#     PermissionDetailView,
#     PermissionListCreateView,
#     RefreshView,
#     RoleDetailView,
#     RoleListCreateView,
#     UserDetailView,
#     UserListCreateView,
# )


# urlpatterns = [
#     path("auth/login/", LoginView.as_view(), name="login"),
#     path("auth/refresh/", RefreshView.as_view(), name="refresh"),
#     path("auth/logout/", LogoutView.as_view(), name="logout"),
#     path("auth/me/", MeView.as_view(), name="me"),
#     path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
#     path("users/", UserListCreateView.as_view(), name="user-list"),
#     path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
#     path("customers/", CustomerListCreateView.as_view(), name="customer-list"),
#     path("customers/<int:pk>/", CustomerDetailView.as_view(), name="customer-detail"),
#     path("roles/", RoleListCreateView.as_view(), name="role-list"),
#     path("roles/<int:pk>/", RoleDetailView.as_view(), name="role-detail"),
#     path("permissions/", PermissionListCreateView.as_view(), name="permission-list"),
#     path("permissions/<int:pk>/", PermissionDetailView.as_view(), name="permission-detail"),
# ]
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/refresh/', views.RefreshView.as_view(), name='refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Users
    path('users/', views.UserListCreateView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # Roles
    path('roles/', views.RoleListCreateView.as_view(), name='role-list'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    
    # Permissions
    path('permissions/', views.PermissionListCreateView.as_view(), name='permission-list'),
    path('permissions/<int:pk>/', views.PermissionDetailView.as_view(), name='permission-detail'),
]