# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

# from .models import AppPermission, Customer, Role, User


# @admin.register(AppPermission)
# class AppPermissionAdmin(admin.ModelAdmin):
#     list_display = ("name", "is_active", "created_at")
#     search_fields = ("name", "description")
#     list_filter = ("is_active", "created_at")


# @admin.register(Role)
# class RoleAdmin(admin.ModelAdmin):
#     list_display = ("name", "is_active", "created_at")
#     search_fields = ("name", "description")
#     list_filter = ("is_active", "created_at")
#     filter_horizontal = ("permissions",)


# @admin.register(User)
# class UserAdmin(DjangoUserAdmin):
#     ordering = ("email",)
#     list_display = ("email", "full_name", "role", "is_staff", "is_active", "created_at")
#     search_fields = ("email", "full_name")
#     readonly_fields = ("last_login", "created_at", "updated_at")

#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Profile", {"fields": ("full_name", "role")}),
#         ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
#         ("Dates", {"fields": ("last_login", "created_at", "updated_at")}),
#     )

#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": ("email", "full_name", "role", "password1", "password2", "is_staff", "is_superuser"),
#             },
#         ),
#     )


# @admin.register(Customer)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ("full_name", "email", "phone_number", "company_name", "is_active", "created_at")
#     search_fields = ("first_name", "last_name", "email", "phone_number", "company_name")
#     list_filter = ("is_active", "created_at")
