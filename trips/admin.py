from django.contrib import admin
from .models import Trip, Destination


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "code")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("driver", "vehicle", "from_label", "to_label", "trip_date", "amount_paid")
    list_filter = ("trip_date", "driver", "vehicle")
    search_fields = ("driver__full_name", "vehicle__plate_number", "purpose")
    autocomplete_fields = ("driver", "vehicle", "from_destination", "to_destination")
