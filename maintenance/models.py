from decimal import Decimal
from django.db import models
from django.utils import timezone
from datetime import timedelta


SERVICE_ROUTINE    = "routine"
SERVICE_TYRE       = "tyre"
SERVICE_ENGINE     = "engine"
SERVICE_ELECTRICAL = "electrical"
SERVICE_BODYWORK   = "bodywork"
SERVICE_BRAKES     = "brakes"
SERVICE_OIL        = "oil"
SERVICE_GENERAL    = "general_service"
SERVICE_OTHER      = "other"

SERVICE_CHOICES = [
    (SERVICE_ROUTINE,    "Routine Service"),
    (SERVICE_TYRE,       "Tyre Change"),
    (SERVICE_ENGINE,     "Engine Repair"),
    (SERVICE_ELECTRICAL, "Electrical"),
    (SERVICE_BODYWORK,   "Bodywork"),
    (SERVICE_BRAKES,     "Brakes"),
    (SERVICE_OIL,        "Oil / Lubricants"),
    (SERVICE_GENERAL,    "General Service"),
    (SERVICE_OTHER,      "Other"),
]

# Which service types apply to which asset kinds.
# Used by the maintenance form to filter the dropdown when the user switches
# between Vehicle and Generator. Reports / aggregations are unaffected.
SERVICE_APPLIES_TO = {
    SERVICE_ROUTINE:    ("vehicle", "generator"),
    SERVICE_TYRE:       ("vehicle",),                # vehicles only
    SERVICE_ENGINE:     ("vehicle", "generator"),
    SERVICE_ELECTRICAL: ("vehicle", "generator"),
    SERVICE_BODYWORK:   ("vehicle",),                # vehicles only
    SERVICE_BRAKES:     ("vehicle",),                # vehicles only
    SERVICE_OIL:        ("vehicle", "generator"),
    SERVICE_GENERAL:    ("vehicle", "generator"),
    SERVICE_OTHER:      ("vehicle", "generator"),
}


class MaintenanceRecord(models.Model):
    """
    A maintenance event for a vehicle. Holds shared fields (vehicle, date,
    vendor, approver). Itemised work and its costs live in related
    MaintenanceItem rows, so a single repair can list multiple services
    with separate costs.

    service_type and total_cost are retained on the record for backwards
    compatibility with existing data and reports:
      - service_type reflects the primary (first) item's category
      - total_cost is auto-set from the sum of items in recompute_total()
    """

    SERVICE_CHOICES = SERVICE_CHOICES

    # A maintenance record is for EITHER a vehicle OR a generator (never both,
    # never neither). The CheckConstraint at the bottom of Meta enforces this.
    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="maintenance_records",
        null=True, blank=True,
        help_text="Set if this record is for a vehicle. Mutually exclusive with generator."
    )
    generator = models.ForeignKey(
        "generators.Generator", on_delete=models.PROTECT, related_name="maintenance_records",
        null=True, blank=True,
        help_text="Set if this record is for a generator. Mutually exclusive with vehicle."
    )
    service_date = models.DateField()

    # Primary service type — mirrors the first line item. Kept on the record so
    # existing reports/filters (which group by service_type) keep working.
    service_type = models.CharField(
        max_length=20, choices=SERVICE_CHOICES, blank=True,
        help_text="Primary service category. Auto-set from the first line item."
    )
    description = models.TextField(
        blank=True,
        help_text="Optional overall summary. Individual work goes in line items."
    )

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

    # Auto-computed from items. editable=False prevents admin/form override.
    total_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"), editable=False,
        help_text="Auto-calculated: sum of all MaintenanceItem costs."
    )
    next_service_date = models.DateField(
        null=True, blank=True,
        help_text="Optional. Triggers dashboard alert within 14 days."
    )

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
        constraints = [
            models.CheckConstraint(
                name="maintenance_one_asset_only",
                check=(
                    models.Q(vehicle__isnull=False, generator__isnull=True) |
                    models.Q(vehicle__isnull=True,  generator__isnull=False)
                ),
            ),
        ]

    def __str__(self):
        return f"{self.asset_label} — {self.service_date}"

    # ── asset helpers (mirror FuelCoupon / FuelLog) ──
    @property
    def is_for_vehicle(self):
        return self.vehicle_id is not None

    @property
    def is_for_generator(self):
        return self.generator_id is not None

    @property
    def asset(self):
        return self.vehicle if self.is_for_vehicle else self.generator

    @property
    def asset_label(self):
        if self.is_for_vehicle:
            return self.vehicle.plate_number
        if self.is_for_generator:
            return self.generator.tag
        return "(no asset)"

    @property
    def asset_kind(self):
        return "vehicle" if self.is_for_vehicle else "generator"

    @property
    def effective_vendor_name(self):
        if self.vendor:
            return self.vendor.name
        return self.vendor_other or "Unknown Vendor"

    @property
    def is_service_due_soon(self):
        if self.next_service_date:
            return self.next_service_date <= (timezone.now().date() + timedelta(days=14))
        return False

    def recompute_total(self):
        """Recompute total_cost and primary service_type from items."""
        total = self.items.aggregate(s=models.Sum("cost"))["s"] or Decimal("0.00")
        self.total_cost = total
        first = self.items.order_by("pk").first()
        if first:
            self.service_type = first.service_type
        # Bypass MaintenanceItem.save's recursion by going straight to super
        super().save(update_fields=["total_cost", "service_type", "updated_at"])


class MaintenanceItem(models.Model):
    """
    A single line of work within a MaintenanceRecord.
    e.g. one record might have: brake pads (₦8,000) + oil change (₦5,000) + tyre rotation (₦2,000)
    """

    record = models.ForeignKey(
        MaintenanceRecord, on_delete=models.CASCADE, related_name="items"
    )
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    description = models.CharField(
        max_length=255,
        help_text="What was done — be specific (e.g. 'Replaced front brake pads')."
    )
    cost = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "maintenance_items"
        ordering = ["pk"]

    def __str__(self):
        return f"{self.get_service_type_display()} — ₦{self.cost}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.record.recompute_total()

    def delete(self, *args, **kwargs):
        record = self.record
        super().delete(*args, **kwargs)
        record.recompute_total()
