from django.db import models


class Vendor(models.Model):

    TYPE_FUEL        = "fuel_station"
    TYPE_MECHANIC    = "mechanic"
    TYPE_TYRE        = "tyre_shop"
    TYPE_ELECTRICAL  = "electrical"
    TYPE_OTHER       = "other"
    TYPE_CHOICES = [
        (TYPE_FUEL,       "Fuel Station"),
        (TYPE_MECHANIC,   "Mechanic / Workshop"),
        (TYPE_TYRE,       "Tyre Shop"),
        (TYPE_ELECTRICAL, "Electrical"),
        (TYPE_OTHER,      "Other"),
    ]

    name      = models.CharField(max_length=150, unique=True)
    type      = models.CharField(max_length=20, choices=TYPE_CHOICES)
    phone     = models.CharField(max_length=20, blank=True)
    address   = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendors"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
