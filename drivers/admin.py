from django.contrib import admin
from .models import Driver

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display  = ["full_name", "staff_id", "phone", "license_no", "license_expiry", "status"]
    list_filter   = ["status", "license_class"]
    search_fields = ["full_name", "staff_id", "license_no"]
