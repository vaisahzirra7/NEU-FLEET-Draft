from django.db import models


class FuelLog(models.Model):
    """
    Records the actual fuel transaction after a coupon is redeemed.
    Saving this record automatically closes (redeems) the linked coupon.
    One FuelLog per coupon — enforced by OneToOneField.

    A fuel log applies to EITHER a vehicle OR a generator (matching the coupon's
    asset). vehicle/driver are populated for vehicle coupons; generator is
    populated for generator coupons. Constraints enforce exclusivity.
    """

    coupon = models.OneToOneField(
        "coupons.FuelCoupon",
        on_delete=models.PROTECT,
        related_name="fuel_log",
        help_text="The coupon being redeemed."
    )

    # ── Asset (auto-filled from coupon) ──
    vehicle     = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="fuel_logs",
        null=True, blank=True,
    )
    generator   = models.ForeignKey(
        "generators.Generator", on_delete=models.PROTECT, related_name="fuel_logs",
        null=True, blank=True,
    )
    # Only set for vehicle coupons
    driver      = models.ForeignKey(
        "drivers.Driver", on_delete=models.PROTECT, related_name="fuel_logs",
        null=True, blank=True,
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

    fuel_date  = models.DateField(help_text="Date the asset was actually fuelled.")
    notes      = models.TextField(blank=True)
    logged_by  = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="fuel_logs_entered"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "fuel_logs"
        ordering = ["-fuel_date"]
        constraints = [
            # Exactly one of vehicle / generator must be set
            models.CheckConstraint(
                name="fuellog_one_asset_only",
                check=(
                    models.Q(vehicle__isnull=False, generator__isnull=True) |
                    models.Q(vehicle__isnull=True,  generator__isnull=False)
                ),
            ),
        ]

    def __str__(self):
        return f"FuelLog #{self.pk} — {self.asset_label} on {self.fuel_date}"

    # ── asset helpers (mirror FuelCoupon for consistency) ──
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

    def save(self, *args, **kwargs):
        # On first save, mirror the coupon's asset (vehicle+driver OR generator)
        if not self.pk:
            if self.coupon.is_for_vehicle:
                self.vehicle = self.coupon.vehicle
                self.driver  = self.coupon.driver
                self.generator = None
            elif self.coupon.is_for_generator:
                self.generator = self.coupon.generator
                self.vehicle = None
                self.driver  = None
            if not self.fuel_station:
                self.fuel_station = self.coupon.fuel_station

        super().save(*args, **kwargs)

        # Mark the coupon as Redeemed after the fuel log is saved.
        # Both Approved (new workflow) and Issued (legacy) coupons are redeemable.
        if self.coupon.status in ("approved", "issued"):
            self.coupon.status = "redeemed"
            self.coupon.save(update_fields=["status", "updated_at"])
