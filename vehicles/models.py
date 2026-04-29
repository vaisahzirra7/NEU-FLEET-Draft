from django.db import models
from accounts.models import Department


class Vehicle(models.Model):

    STATUS_ACTIVE       = "active"
    STATUS_UNDER_REPAIR = "under_repair"
    STATUS_INACTIVE     = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE,       "Active"),
        (STATUS_UNDER_REPAIR, "Under Repair"),
        (STATUS_INACTIVE,     "Inactive"),
    ]

    FUEL_PETROL = "petrol"
    FUEL_DIESEL = "diesel"
    FUEL_CHOICES = [
        (FUEL_PETROL, "Petrol"),
        (FUEL_DIESEL, "Diesel"),
    ]

    TYPE_CHOICES = [
        ("car",        "Car"),
        ("bus",        "Bus"),
        ("van",        "Van"),
        ("truck",      "Truck"),
        ("motorcycle", "Motorcycle"),
        ("other",      "Other"),
    ]

    # ── identity ──
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    make         = models.CharField(max_length=100, help_text="Manufacturer, e.g. Toyota")
    model        = models.CharField(max_length=100, help_text="Model name, e.g. Hilux")
    year         = models.PositiveSmallIntegerField(help_text="Year of manufacture")
    colour       = models.CharField(max_length=50, blank=True)
    engine_no    = models.CharField(max_length=100, blank=True)
    chassis_no   = models.CharField(max_length=100, blank=True)
    fuel_type    = models.CharField(max_length=10, choices=FUEL_CHOICES)

    # ── ownership ──
    department     = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name="vehicles"
    )
    # default_driver set as FK in drivers app via string reference to avoid circular import
    default_driver = models.ForeignKey(
        "drivers.Driver",
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name="default_vehicle"
    )

    # ── status ──
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    notes  = models.TextField(blank=True)

    # ── meta ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicles"
        ordering = ["plate_number"]

    def __str__(self):
        return f"{self.plate_number} — {self.make} {self.model}"

    @property
    def display_name(self):
        return f"{self.plate_number} ({self.make} {self.model})"

    def decommission(self):
        self.status = self.STATUS_INACTIVE
        self.save(update_fields=["status", "updated_at"])
