from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display  = ["plate_number", "make", "model", "year", "department", "status"]
    list_filter   = ["status", "vehicle_type", "fuel_type", "department"]
    search_fields = ["plate_number", "make", "model"]
