from django.db import models


class FuelLog(models.Model):
    """
    Records the actual fuel transaction after a coupon is redeemed.
    Saving this record automatically closes (redeems) the linked coupon.
    One FuelLog per coupon — enforced by OneToOneField.
    """

    coupon = models.OneToOneField(
        "coupons.FuelCoupon",
        on_delete=models.PROTECT,
        related_name="fuel_log",
        help_text="The coupon being redeemed. Must be in 'Issued' status."
    )

    # Auto-filled from coupon but stored for query efficiency
    vehicle     = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="fuel_logs"
    )
    driver      = models.ForeignKey(
        "drivers.Driver", on_delete=models.PROTECT, related_name="fuel_logs"
    )

    # Vendor may differ slightly from what the coupon specified
    fuel_station = models.ForeignKey(
        "vendors.Vendor", on_delete=models.PROTECT, related_name="fuel_logs",
        null=True, blank=True,
        help_text="Defaults to coupon's fuel station. Editable if station differed."
    )

    # Actuals — may differ slightly from coupon amounts
    actual_litres = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="Actual litres dispensed. May be less than coupon amount."
    )
    actual_cost = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Actual total cost paid."
    )

    fuel_date  = models.DateField(help_text="Date the vehicle was actually fuelled.")
    notes      = models.TextField(blank=True)
    logged_by  = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="fuel_logs_entered"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fuel_logs"
        ordering = ["-fuel_date"]

    def __str__(self):
        return f"FuelLog #{self.pk} — {self.vehicle.plate_number} on {self.fuel_date}"

    def save(self, *args, **kwargs):
        # On first save, auto-fill vehicle and driver from coupon
        if not self.pk:
            self.vehicle = self.coupon.vehicle
            self.driver  = self.coupon.driver
            if not self.fuel_station:
                self.fuel_station = self.coupon.fuel_station

        super().save(*args, **kwargs)

        # Mark the coupon as Redeemed after the fuel log is saved
        if self.coupon.status == "issued":
            self.coupon.status = "redeemed"
            self.coupon.save(update_fields=["status", "updated_at"])
