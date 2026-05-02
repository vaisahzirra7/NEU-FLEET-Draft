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

    STATUS_ISSUED    = "issued"
    STATUS_REDEEMED  = "redeemed"
    STATUS_CANCELLED = "cancelled"
    STATUS_EXPIRED   = "expired"
    STATUS_CHOICES = [
        (STATUS_ISSUED,    "Issued"),
        (STATUS_REDEEMED,  "Redeemed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_EXPIRED,   "Expired"),
    ]

    # ── identifiers ──
    # Human-readable sequential ID is generated in save() via a signal/override
    coupon_id         = models.CharField(max_length=25, unique=True, editable=False)
    verification_code = models.CharField(max_length=10, unique=True, editable=False)

    # ── linked records ──
    vehicle     = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="coupons"
    )
    driver      = models.ForeignKey(
        "drivers.Driver", on_delete=models.PROTECT, related_name="coupons"
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

    # ── lifecycle ──
    status              = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_ISSUED)
    issue_datetime      = models.DateTimeField(auto_now_add=True)
    expiry_date         = models.DateField(
        null=True, blank=True,
        help_text="Optional. Set per coupon at issuance. If blank, no expiry applies."
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Required when status is set to Cancelled."
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

    def __str__(self):
        return f"{self.coupon_id} — {self.vehicle.plate_number} ({self.status})"

    # ── lifecycle helpers ──
    @property
    def is_open(self):
        return self.status == self.STATUS_ISSUED

    @property
    def is_expired_by_date(self):
        """Has the optional expiry date passed without redemption?"""
        if self.expiry_date and self.status == self.STATUS_ISSUED:
            return timezone.now().date() > self.expiry_date
        return False

    def cancel(self, reason=""):
        self.status = self.STATUS_CANCELLED
        self.cancellation_reason = reason
        self.save(update_fields=["status", "cancellation_reason", "updated_at"])

    def mark_expired(self):
        self.status = self.STATUS_EXPIRED
        self.save(update_fields=["status", "updated_at"])

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
