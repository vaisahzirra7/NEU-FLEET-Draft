from django.db import models


class Generator(models.Model):
    """
    A generator (electromechanical device producing electrical power).
    Tracked for fuel issuance, maintenance, and lifecycle reporting.
    """

    STATUS_ACTIVE       = "active"
    STATUS_UNDER_REPAIR = "under_repair"
    STATUS_INACTIVE     = "inactive"
    STATUS_CHOICES = [
        (STATUS_ACTIVE,       "Active"),
        (STATUS_UNDER_REPAIR, "Under Repair"),
        (STATUS_INACTIVE,     "Inactive (Decommissioned)"),
    ]

    FUEL_PETROL = "petrol"
    FUEL_DIESEL = "diesel"
    FUEL_CHOICES = [
        (FUEL_DIESEL, "Diesel"),
        (FUEL_PETROL, "Petrol"),
    ]

    # ── identity ──
    tag           = models.CharField(
        max_length=30, unique=True,
        help_text="Unique identifier, e.g. 'GEN-LIB-01'."
    )
    name          = models.CharField(
        max_length=150,
        help_text="Human-friendly label, e.g. 'Library Main Generator'."
    )
    make          = models.CharField(max_length=100, help_text="Manufacturer, e.g. Mikano, Caterpillar.")
    model         = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    kva_rating    = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="Power rating in kVA, e.g. 250.00"
    )
    fuel_type           = models.CharField(max_length=10, choices=FUEL_CHOICES, default=FUEL_DIESEL)
    tank_capacity_litres = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Optional. Maximum fuel tank capacity in litres."
    )

    # ── ownership / location ──
    # Free-text building name. No FK to Department — generators are
    # organisation-wide visible to anyone with the 'generators' read permission.
    building       = models.CharField(
        max_length=150,
        help_text="Name of the building this generator serves, e.g. 'Library', 'Senate Block'."
    )
    location_note  = models.CharField(
        max_length=200, blank=True,
        help_text="Optional. More specific location within the building (e.g. 'Ground floor utility room')."
    )

    # ── lifecycle ──
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    needs_monthly_fuel = models.BooleanField(
        default=False,
        help_text="Flag generators that should receive fuel every month. Used for monthly-fuel reminders."
    )
    installed_date = models.DateField(null=True, blank=True, help_text="Optional. Date the generator was installed/commissioned.")
    notes          = models.TextField(blank=True)

    # ── meta ──
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "generators"
        ordering = ["tag"]

    def __str__(self):
        return f"{self.tag} — {self.name}"

    @property
    def display_name(self):
        return f"{self.tag} ({self.name})"

    def decommission(self):
        self.status = self.STATUS_INACTIVE
        self.save(update_fields=["status", "updated_at"])
