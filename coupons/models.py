import uuid
import random
import string
from django.db import models
from django.utils import timezone


def generate_verification_code():
    """Generates a short alphanumeric code, e.g. X7K2-P9QR"""
    chars = string.ascii_uppercase + string.digits
    part1 = "".join(random.choices(chars, k=4))
    part2 = "".join(random.choices(chars, k=4))
    return f"{part1}-{part2}"


class FuelCoupon(models.Model):

    STATUS_PENDING   = "pending"
    STATUS_APPROVED  = "approved"
    STATUS_REJECTED  = "rejected"
    STATUS_ISSUED    = "issued"      # legacy/deprecated: pre-workflow records. Treat as approved.
    STATUS_REDEEMED  = "redeemed"
    STATUS_CANCELLED = "cancelled"
    STATUS_EXPIRED   = "expired"
    STATUS_CHOICES = [
        (STATUS_PENDING,   "Pending Approval"),
        (STATUS_APPROVED,  "Approved"),
        (STATUS_REJECTED,  "Rejected"),
        (STATUS_ISSUED,    "Issued"),
        (STATUS_REDEEMED,  "Redeemed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_EXPIRED,   "Expired"),
    ]

    # Statuses that count as a financial expense (i.e. money committed/spent).
    # Used by reports to exclude pending/rejected from totals.
    EXPENSE_STATUSES = (STATUS_APPROVED, STATUS_REDEEMED, STATUS_ISSUED)

    # Statuses that are "live" — can still be redeemed.
    REDEEMABLE_STATUSES = (STATUS_APPROVED, STATUS_ISSUED)

    # ── identifiers ──
    # Human-readable sequential ID is generated in save() via a signal/override
    coupon_id         = models.CharField(max_length=25, unique=True, editable=False)
    verification_code = models.CharField(max_length=10, unique=True, editable=False)

    # ── linked asset ──
    # A coupon is issued for EITHER a vehicle OR a generator (never both, never neither).
    # The CheckConstraint at the bottom of Meta enforces this exclusivity.
    vehicle     = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="coupons",
        null=True, blank=True,
        help_text="Set if this coupon is for a vehicle. Mutually exclusive with generator."
    )
    generator   = models.ForeignKey(
        "generators.Generator", on_delete=models.PROTECT, related_name="coupons",
        null=True, blank=True,
        help_text="Set if this coupon is for a generator. Mutually exclusive with vehicle."
    )
    # Driver only applies when the coupon is for a vehicle. Generators have no driver.
    driver      = models.ForeignKey(
        "drivers.Driver", on_delete=models.PROTECT, related_name="coupons",
        null=True, blank=True,
        help_text="Driver who will collect the fuel. Required for vehicle coupons; null for generator coupons."
    )
    fuel_station = models.ForeignKey(
        "vendors.Vendor", on_delete=models.PROTECT, related_name="coupons",
        limit_choices_to={"type": "fuel_station", "is_active": True}
    )
    issued_by   = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="issued_coupons"
    )

    # ── fuel details ──
    litres         = models.DecimalField(max_digits=8, decimal_places=2)
    cost_per_litre = models.DecimalField(max_digits=8, decimal_places=2)
    total_value    = models.DecimalField(
        max_digits=10, decimal_places=2, editable=False,
        help_text="Auto-calculated: litres x cost_per_litre"
    )

    # Original requested litres — preserved if the approver edits the litres on approval.
    # NULL means the litres were never changed from what was issued.
    requested_litres = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True, editable=False,
        help_text="Original litres requested at issue, if the approver edited the amount."
    )

    # ── lifecycle ──
    status              = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    issue_datetime      = models.DateTimeField(auto_now_add=True)
    expiry_date         = models.DateField(
        null=True, blank=True,
        help_text="Optional. Set per coupon at issuance. If blank, no expiry applies."
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Required when status is set to Cancelled."
    )

    # ── approval workflow ──
    approved_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, null=True, blank=True,
        related_name="approved_coupons",
        help_text="User who approved or rejected this coupon."
    )
    approved_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the approval/rejection decision was made."
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Optional reason supplied by the approver when rejecting."
    )
    self_approved = models.BooleanField(
        default=False,
        help_text="True if the issuer approved their own coupon. Surfaced in audit."
    )

    # ── optional note ──
    purpose = models.CharField(
        max_length=255, blank=True,
        help_text="Brief note on why fuel is being issued, e.g. 'VC airport run'."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "fuel_coupons"
        ordering = ["-issue_datetime"]
        constraints = [
            # Exactly one of vehicle / generator must be set.
            models.CheckConstraint(
                name="coupon_one_asset_only",
                check=(
                    models.Q(vehicle__isnull=False, generator__isnull=True) |
                    models.Q(vehicle__isnull=True,  generator__isnull=False)
                ),
            ),
            # Driver can only be set if vehicle is set (generators have no driver).
            models.CheckConstraint(
                name="coupon_driver_only_with_vehicle",
                check=(
                    models.Q(vehicle__isnull=False) |
                    models.Q(driver__isnull=True)
                ),
            ),
        ]

    def __str__(self):
        return f"{self.coupon_id} — {self.asset_label} ({self.status})"

    # ── asset helpers ──
    @property
    def is_for_vehicle(self):
        return self.vehicle_id is not None

    @property
    def is_for_generator(self):
        return self.generator_id is not None

    @property
    def asset(self):
        """Returns the linked vehicle or generator object, whichever is set."""
        return self.vehicle if self.is_for_vehicle else self.generator

    @property
    def asset_label(self):
        """Short label for displays (plate number for vehicles, tag for generators)."""
        if self.is_for_vehicle:
            return self.vehicle.plate_number
        if self.is_for_generator:
            return self.generator.tag
        return "(no asset)"

    @property
    def asset_kind(self):
        """Returns 'vehicle' or 'generator'."""
        return "vehicle" if self.is_for_vehicle else "generator"

    @property
    def asset_context_value(self):
        """
        Returns the context value to display alongside the asset:
        - vehicle coupons: driver name
        - generator coupons: building name
        """
        if self.is_for_vehicle:
            return self.driver.full_name if self.driver_id else "(no driver)"
        if self.is_for_generator:
            return self.generator.building
        return ""

    # ── lifecycle helpers ──
    @property
    def is_open(self):
        """Live coupon — approved or legacy-issued, not redeemed/cancelled/expired."""
        return self.status in self.REDEEMABLE_STATUSES

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    @property
    def is_printable(self):
        """Print slip is only available once approved (or for legacy issued records)."""
        return self.status in (self.STATUS_APPROVED, self.STATUS_ISSUED, self.STATUS_REDEEMED)

    @property
    def is_expired_by_date(self):
        """Has the optional expiry date passed without redemption?"""
        if self.expiry_date and self.status in self.REDEEMABLE_STATUSES:
            return timezone.now().date() > self.expiry_date
        return False

    def cancel(self, reason=""):
        self.status = self.STATUS_CANCELLED
        self.cancellation_reason = reason
        self.save(update_fields=["status", "cancellation_reason", "updated_at"])

    def mark_expired(self):
        self.status = self.STATUS_EXPIRED
        self.save(update_fields=["status", "updated_at"])

    def approve(self, approver, new_litres=None, new_cost_per_litre=None):
        """
        Approve a pending coupon. Optionally adjust litres and/or cost-per-litre.
        Stores original litres in requested_litres if changed.
        Cost-per-litre changes are not persisted as a separate "original" column
        (no DB field for it), but the live total_value is recalculated and the
        view captures the edit in the audit log detail.
        Flags self_approved if approver is the issuer.
        """
        if self.status != self.STATUS_PENDING:
            raise ValueError(f"Cannot approve a coupon with status '{self.status}'.")

        # Track pre-edit cost so the view can audit any change.
        # Set as a transient attribute (not a DB column).
        self._previous_cost_per_litre = self.cost_per_litre

        if new_litres is not None and new_litres != self.litres:
            self.requested_litres = self.litres
            self.litres = new_litres
        if new_cost_per_litre is not None and new_cost_per_litre != self.cost_per_litre:
            self.cost_per_litre = new_cost_per_litre
        # save() recomputes total_value
        self.status = self.STATUS_APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.self_approved = (approver == self.issued_by)
        self.save()

    # ── Aliases so views/templates can use either naming convention ──
    @property
    def is_self_approved(self):
        return self.self_approved

    @property
    def original_litres(self):
        return self.requested_litres

    @property
    def original_cost_per_litre(self):
        """Returns the previous cost_per_litre captured during approve(), or None."""
        return getattr(self, "_previous_cost_per_litre", None)

    @property
    def was_edited_by_approver(self):
        """True if approver changed litres (cost edits are audited but not stored)."""
        return self.requested_litres is not None and self.requested_litres != self.litres

    def reject(self, approver, reason=""):
        if self.status != self.STATUS_PENDING:
            raise ValueError(f"Cannot reject a coupon with status '{self.status}'.")
        self.status = self.STATUS_REJECTED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.self_approved = (approver == self.issued_by)
        self.save(update_fields=[
            "status", "approved_by", "approved_at",
            "rejection_reason", "self_approved", "updated_at",
        ])

    # ── save override — compute total and generate IDs ──
    def save(self, *args, **kwargs):
        # Compute total value
        if self.litres and self.cost_per_litre:
            self.total_value = self.litres * self.cost_per_litre

        # Generate coupon_id on first save
        if not self.coupon_id:
            # Format: NEU/FMS/CP/XXXXXXXX
            # 8-char random alphanumeric suffix — not sequential, not guessable
            chars = string.ascii_uppercase + string.digits
            candidate = "NEU/FMS/CP/" + "".join(random.choices(chars, k=8))
            # Guarantee uniqueness (collision probability is negligible but guard anyway)
            while FuelCoupon.objects.filter(coupon_id=candidate).exists():
                candidate = "NEU/FMS/CP/" + "".join(random.choices(chars, k=8))
            self.coupon_id = candidate

        # Generate verification code on first save
        if not self.verification_code:
            code = generate_verification_code()
            # Ensure uniqueness
            while FuelCoupon.objects.filter(verification_code=code).exists():
                code = generate_verification_code()
            self.verification_code = code

        super().save(*args, **kwargs)
