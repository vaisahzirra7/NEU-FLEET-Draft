from django.contrib import admin
from .models import Generator


@admin.register(Generator)
class GeneratorAdmin(admin.ModelAdmin):
    list_display  = ("tag", "name", "make", "model", "kva_rating", "fuel_type", "building", "status")
    list_filter   = ("status", "fuel_type")
    search_fields = ("tag", "name", "make", "model", "serial_number", "building")
    ordering      = ("tag",)
