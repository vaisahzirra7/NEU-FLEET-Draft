from django.contrib import admin
from .models import Vendor

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display  = ["name", "type", "phone", "is_active"]
    list_filter   = ["type", "is_active"]
    search_fields = ["name"]
