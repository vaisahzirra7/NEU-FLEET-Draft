from decimal import Decimal
from django.db import models
from django.db.models import Sum


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

    # ───────────────────────────────────────────────────────────────────────
    # Fuel-station ledger
    # ───────────────────────────────────────────────────────────────────────
    # Only meaningful for vendors of type=fuel_station. For other vendor
    # types these properties return 0 / are not used in the UI.

    @property
    def total_deposits(self):
        """Sum of all deposits (including negative corrections if added later)."""
        if self.type != self.TYPE_FUEL:
            return Decimal("0.00")
        agg = self.deposits.aggregate(t=Sum("amount"))
        return agg["t"] or Decimal("0.00")

    @property
    def total_redeemed_value(self):
        """
        Sum of coupon total_value for THIS station where status=redeemed.
        Only redeemed coupons count — matches the "expense only when redeemed"
        rule established for the reports module.
        """
        if self.type != self.TYPE_FUEL:
            return Decimal("0.00")
        from coupons.models import FuelCoupon
        agg = FuelCoupon.objects.filter(
            fuel_station=self,
            status=FuelCoupon.STATUS_REDEEMED,
        ).aggregate(t=Sum("total_value"))
        return agg["t"] or Decimal("0.00")

    @property
    def total_outstanding_value(self):
        """
        Sum of coupon total_value for THIS station where the coupon is
        still in the pipeline (pending approval, approved/issued but
        not yet redeemed). All such coupons reserve money against the
        balance so they can't be double-spent.

        Excluded: redeemed (already deducted), rejected, cancelled, expired.
        """
        if self.type != self.TYPE_FUEL:
            return Decimal("0.00")
        from coupons.models import FuelCoupon
        agg = FuelCoupon.objects.filter(
            fuel_station=self,
            status__in=(
                FuelCoupon.STATUS_PENDING,
                FuelCoupon.STATUS_APPROVED,
                FuelCoupon.STATUS_ISSUED,
            ),
        ).aggregate(t=Sum("total_value"))
        return agg["t"] or Decimal("0.00")

    @property
    def balance(self):
        """
        "Book balance" — what's been put in minus what's been used.
        deposits - redeemed.

        This is the right number for "how much fuel did we actually pay for
        and consume at this station." Doesn't reserve outstanding coupons,
        so it overstates available cash by the outstanding amount.
        """
        return self.total_deposits - self.total_redeemed_value

    @property
    def available_balance(self):
        """
        "Available for new coupons" — the balance MINUS any outstanding
        coupons already promised against the station. This is what the
        issuance check uses.
        """
        return self.balance - self.total_outstanding_value

    @property
    def is_low_balance(self):
        """True if available balance is below the global threshold."""
        if self.type != self.TYPE_FUEL or not self.is_active:
            return False
        try:
            from system_settings.models import SystemSettings
            threshold = SystemSettings.get().low_balance_threshold or Decimal("0.00")
        except Exception:
            threshold = Decimal("0.00")
        return self.available_balance < threshold
