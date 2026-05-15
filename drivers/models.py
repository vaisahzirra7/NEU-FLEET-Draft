from django.db import models
from django.utils import timezone
from datetime import timedelta


class Driver(models.Model):

    STATUS_ACTIVE   = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE,   "Active"),
        (STATUS_INACTIVE, "Inactive"),
    ]

    PAY_SALARIED = "salaried"
    PAY_PER_TRIP = "per_trip"
    PAY_MIXED    = "mixed"
    PAY_CHOICES = [
        (PAY_SALARIED, "Salaried"),
        (PAY_PER_TRIP, "Paid per Trip"),
        (PAY_MIXED,    "Mixed (Salary + Trip)"),
    ]

    LICENSE_CLASSES = [
        ("A",  "Class A"),
        ("B",  "Class B"),
        ("C",  "Class C"),
        ("D",  "Class D"),
        ("E",  "Class E"),
        ("G",  "Class G"),
    ]

    full_name       = models.CharField(max_length=150)
    staff_id        = models.CharField(max_length=50, unique=True)
    phone           = models.CharField(max_length=20)
    license_no      = models.CharField(max_length=50, unique=True)
    license_class   = models.CharField(max_length=5, choices=LICENSE_CLASSES)
    license_expiry  = models.DateField(help_text="Used to trigger 30-day expiry alert.")
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    payment_type    = models.CharField(
        max_length=15, choices=PAY_CHOICES, default=PAY_SALARIED,
        help_text="How this driver is paid. Affects trip-logging defaults."
    )
    notes           = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "drivers"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.staff_id})"

    @property
    def is_license_expiring_soon(self):
        """True if license expires within 30 days from today."""
        return (
            self.status == self.STATUS_ACTIVE
            and self.license_expiry <= (timezone.now().date() + timedelta(days=30))
        )

    @property
    def is_license_expired(self):
        return self.license_expiry < timezone.now().date()

    @property
    def days_until_license_expiry(self):
        delta = self.license_expiry - timezone.now().date()
        return delta.days


class DriverLicenceRenewal(models.Model):
    """Records each time a driver's licence is renewed."""
    driver          = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="licence_renewals")
    new_license_no  = models.CharField(max_length=50, help_text="New licence number (can be same if renewal)")
    new_expiry      = models.DateField(help_text="New expiry date after renewal")
    renewed_by      = models.CharField(max_length=150, help_text="Name of staff who recorded this renewal")
    notes           = models.TextField(blank=True)
    renewed_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "driver_licence_renewals"
        ordering = ["-renewed_at"]

    def __str__(self):
        return f"{self.driver.full_name} — renewed {self.new_expiry}"
