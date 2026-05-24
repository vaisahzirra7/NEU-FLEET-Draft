from decimal import Decimal
from django.db import models


class StationDeposit(models.Model):
    """
    A deposit of money into a fuel station's ledger.

    Per the financial-control rules established for this feature:
      - Deposits are immutable. They cannot be edited.
      - Super Admin can DELETE an erroneous deposit (e.g. typo). The audit
        log captures the deletion, including who deleted it and the amount.
      - There is no negative-correction pattern — deletion is the only
        recovery mechanism for mistakes.

    Balance = sum of all deposits for a station minus the sum of redeemed
    coupon values for that station. Computed on the Vendor model
    (vendor.balance / vendor.available_balance).
    """

    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        related_name="deposits",
        limit_choices_to={"type": "fuel_station"},
        help_text="The fuel station receiving this deposit.",
    )
    amount = models.DecimalField(
        max_digits=14, decimal_places=2,
        help_text="Amount deposited. Must be a positive number.",
    )
    deposit_date = models.DateField(
        help_text="The date the deposit was made at the bank / station.",
    )
    reference_number = models.CharField(
        max_length=80, blank=True, default="",
        help_text="Bank reference, transfer slip number, teller ID, etc. Optional but recommended.",
    )
    note = models.TextField(
        blank=True, default="",
        help_text="Optional note: source of funds, purpose, context.",
    )

    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT,
        related_name="deposits_made",
        help_text="The admin who recorded this deposit.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "station_deposits"
        ordering = ["-deposit_date", "-created_at"]
        indexes = [
            models.Index(fields=["vendor", "-deposit_date"]),
        ]

    def __str__(self):
        return f"₦{self.amount} → {self.vendor.name} on {self.deposit_date}"
