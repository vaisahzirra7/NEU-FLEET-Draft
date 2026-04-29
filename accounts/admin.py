from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Department, Role, RoleModulePermission, User


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ["name", "code", "is_active", "created_at"]
    list_filter   = ["is_active"]
    search_fields = ["name", "code"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display  = ["name", "is_system_role", "created_at"]
    list_filter   = ["is_system_role"]


@admin.register(RoleModulePermission)
class RoleModulePermissionAdmin(admin.ModelAdmin):
    list_display  = ["role", "module", "can_read", "can_write", "can_edit", "can_delete"]
    list_filter   = ["role", "module"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display   = ["email", "full_name", "role", "department", "is_active", "is_system_admin"]
    list_filter    = ["is_active", "is_system_admin", "role"]
    search_fields  = ["email", "full_name"]
    ordering       = ["full_name"]
    fieldsets = (
        (None,           {"fields": ("email", "password")}),
        ("Personal",     {"fields": ("full_name", "role", "department")}),
        ("Permissions",  {"fields": ("is_active", "is_staff", "is_system_admin", "is_superuser")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "full_name", "password1", "password2", "role", "department", "is_system_admin")}),
    )
