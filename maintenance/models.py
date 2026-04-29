from django.db import models
from django.utils import timezone
from datetime import timedelta


class MaintenanceRecord(models.Model):

    SERVICE_ROUTINE    = "routine"
    SERVICE_TYRE       = "tyre"
    SERVICE_ENGINE     = "engine"
    SERVICE_ELECTRICAL = "electrical"
    SERVICE_BODYWORK   = "bodywork"
    SERVICE_OTHER      = "other"
    SERVICE_CHOICES = [
        (SERVICE_ROUTINE,    "Routine Service"),
        (SERVICE_TYRE,       "Tyre Change"),
        (SERVICE_ENGINE,     "Engine Repair"),
        (SERVICE_ELECTRICAL, "Electrical"),
        (SERVICE_BODYWORK,   "Bodywork"),
        (SERVICE_OTHER,      "Other"),
    ]

    vehicle      = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="maintenance_records"
    )
    service_date = models.DateField()
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    description  = models.TextField(help_text="What was done — be specific.")

    # Vendor: from register OR a one-off external vendor (free text)
    vendor = models.ForeignKey(
        "vendors.Vendor", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="maintenance_records",
        help_text="Select from vendor register, or leave blank and use vendor_other."
    )
    vendor_other = models.CharField(
        max_length=150, blank=True,
        help_text="Free-text for one-off / external vendors not in the register."
    )

    total_cost       = models.DecimalField(max_digits=12, decimal_places=2)
    next_service_date = models.DateField(
        null=True, blank=True,
        help_text="Optional. Triggers dashboard alert within 14 days."
    )

    # Simple text field — no workflow, just records who sanctioned it
    approved_by = models.CharField(
        max_length=150,
        help_text="Name or designation of whoever authorised this expenditure."
    )
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="maintenance_records"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "maintenance_records"
        ordering = ["-service_date"]

    def __str__(self):
        return f"{self.vehicle.plate_number} — {self.get_service_type_display()} on {self.service_date}"

    @property
    def effective_vendor_name(self):
        """Returns vendor name from register or the free-text fallback."""
        if self.vendor:
            return self.vendor.name
        return self.vendor_other or "Unknown Vendor"

    @property
    def is_service_due_soon(self):
        """True if next service date is within 14 days from today."""
        if self.next_service_date:
            return self.next_service_date <= (timezone.now().date() + timedelta(days=14))
        return False
