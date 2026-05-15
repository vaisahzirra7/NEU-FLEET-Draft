from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0004_rolemodulepermission_can_approve_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Generator",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tag", models.CharField(help_text="Unique identifier, e.g. 'GEN-LIB-01'.", max_length=30, unique=True)),
                ("name", models.CharField(help_text="Human-friendly label, e.g. 'Library Main Generator'.", max_length=150)),
                ("make", models.CharField(help_text="Manufacturer, e.g. Mikano, Caterpillar.", max_length=100)),
                ("model", models.CharField(blank=True, max_length=100)),
                ("serial_number", models.CharField(blank=True, max_length=100)),
                ("kva_rating", models.DecimalField(decimal_places=2, help_text="Power rating in kVA, e.g. 250.00", max_digits=8)),
                (
                    "fuel_type",
                    models.CharField(
                        choices=[("diesel", "Diesel"), ("petrol", "Petrol")],
                        default="diesel", max_length=10,
                    ),
                ),
                (
                    "tank_capacity_litres",
                    models.DecimalField(
                        blank=True, decimal_places=2,
                        help_text="Optional. Maximum fuel tank capacity in litres.",
                        max_digits=8, null=True,
                    ),
                ),
                ("location_note", models.CharField(blank=True, help_text="Optional. More specific location within the building (e.g. 'Ground floor utility room').", max_length=200)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("active", "Active"),
                            ("under_repair", "Under Repair"),
                            ("inactive", "Inactive (Decommissioned)"),
                        ],
                        default="active", max_length=20,
                    ),
                ),
                ("installed_date", models.DateField(blank=True, help_text="Optional. Date the generator was installed/commissioned.", null=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "department",
                    models.ForeignKey(
                        help_text="Building/Department that owns or hosts this generator.",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="generators",
                        to="accounts.department",
                    ),
                ),
            ],
            options={
                "db_table": "generators",
                "ordering": ["tag"],
            },
        ),
    ]
