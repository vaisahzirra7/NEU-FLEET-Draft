from django.db import models
from django.utils import timezone


class Destination(models.Model):
    """
    Managed list of common from/to points used when logging trips.
    Admins maintain this list; trip-loggers can also enter a one-off
    free-text destination via the Trip.from_other / to_other fields.
    """
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(
        max_length=20, blank=True,
        help_text="Optional short code, e.g. 'GMB', 'ABJ'."
    )
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="created_destinations",
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "destinations"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Trip(models.Model):
    """
    A paid driver trip. Records origin, destination, amount paid,
    optional link to fuel coupons consumed on the trip.
    """

    driver = models.ForeignKey(
        "drivers.Driver", on_delete=models.PROTECT, related_name="trips"
    )
    vehicle = models.ForeignKey(
        "vehicles.Vehicle", on_delete=models.PROTECT, related_name="trips"
    )

    # Origin
    from_destination = models.ForeignKey(
        Destination, on_delete=models.PROTECT, null=True, blank=True,
        related_name="trips_from",
        help_text="From a registered destination. Leave blank to use from_other."
    )
    from_other = models.CharField(
        max_length=150, blank=True,
        help_text="Free text for one-off origins not in the destination register."
    )

    # Destination
    to_destination = models.ForeignKey(
        Destination, on_delete=models.PROTECT, null=True, blank=True,
        related_name="trips_to",
        help_text="To a registered destination. Leave blank to use to_other."
    )
    to_other = models.CharField(
        max_length=150, blank=True,
        help_text="Free text for one-off destinations not in the register."
    )

    trip_date = models.DateField()
    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2,
        help_text="Amount paid to the driver for this trip."
    )
    purpose = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)

    # Optional link to fuel coupons consumed during the trip
    fuel_coupons = models.ManyToManyField(
        "coupons.FuelCoupon", blank=True, related_name="trips",
        help_text="Optional: which fuel coupons were used for this trip."
    )

    logged_by = models.ForeignKey(
        "accounts.User", on_delete=models.PROTECT, related_name="logged_trips"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trips"
        ordering = ["-trip_date", "-created_at"]

    def __str__(self):
        return f"{self.driver.full_name}: {self.from_label} → {self.to_label} ({self.trip_date})"

    @property
    def from_label(self):
        if self.from_destination:
            return self.from_destination.name
        return self.from_other or "—"

    @property
    def to_label(self):
        if self.to_destination:
            return self.to_destination.name
        return self.to_other or "—"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.from_destination and not self.from_other:
            raise ValidationError({"from_destination": "Origin is required (pick or type)."})
        if not self.to_destination and not self.to_other:
            raise ValidationError({"to_destination": "Destination is required (pick or type)."})
