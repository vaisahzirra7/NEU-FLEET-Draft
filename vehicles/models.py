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
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    needs_monthly_fuel = models.BooleanField(
        default=False,
        help_text="Flag vehicles that should receive fuel every month. Used to generate monthly fuel reminders."
    )
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


class FleetLicenceExpiry(models.Model):
    """
    Singleton model — stores the single fleet-wide vehicle licence expiry date.
    All vehicles are renewed together, so one record covers the whole fleet.
    """
    expiry_date   = models.DateField(help_text="Date the fleet vehicle licences expire.")
    notes         = models.TextField(blank=True)
    updated_at    = models.DateTimeField(auto_now=True)
    updated_by    = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = "fleet_licence_expiry"
        verbose_name = "Fleet Licence Expiry"

    def __str__(self):
        return f"Fleet Licence — expires {self.expiry_date}"

    @classmethod
    def get(cls):
        """Return the singleton instance, or None if not set."""
        return cls.objects.first()

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()

    @property
    def days_until_expiry(self):
        from django.utils import timezone
        return (self.expiry_date - timezone.now().date()).days

    @property
    def is_expiring_soon(self):
        """True if expiring within 60 days."""
        return self.days_until_expiry <= 60


class MonthlyFuelDismissal(models.Model):
    """
    Records when a user dismisses the monthly fuel reminder for a vehicle.
    Prevents the reminder from reappearing until the next month.
    """
    vehicle      = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="fuel_dismissals")
    month        = models.PositiveSmallIntegerField(help_text="Month number (1-12)")
    year         = models.PositiveSmallIntegerField(help_text="Year")
    dismissed_by = models.CharField(max_length=150)
    dismissed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = "monthly_fuel_dismissals"
        unique_together = [["vehicle", "month", "year"]]

    def __str__(self):
        return f"{self.vehicle.plate_number} — {self.month}/{self.year}"


class DriverVehicleAssignment(models.Model):
    """Records every time a driver is assigned/unassigned from a vehicle."""
    vehicle     = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="assignments")
    driver      = models.ForeignKey("drivers.Driver", on_delete=models.SET_NULL, null=True, related_name="vehicle_assignments")
    driver_name = models.CharField(max_length=150, help_text="Snapshot of driver name at time of assignment")
    assigned_by = models.CharField(max_length=150)
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes       = models.TextField(blank=True)

    class Meta:
        db_table = "driver_vehicle_assignments"
        ordering = ["-assigned_at"]

    def __str__(self):
        return f"{self.vehicle.plate_number} → {self.driver_name}"
