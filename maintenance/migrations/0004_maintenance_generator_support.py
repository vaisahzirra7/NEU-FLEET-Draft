from django.db import migrations, models
import django.db.models.deletion


SERVICE_CHOICES = [
    ("routine",         "Routine Service"),
    ("tyre",            "Tyre Change"),
    ("engine",          "Engine Repair"),
    ("electrical",      "Electrical"),
    ("bodywork",        "Bodywork"),
    ("brakes",          "Brakes"),
    ("oil",             "Oil / Lubricants"),
    ("general_service", "General Service"),
    ("other",           "Other"),
]


class Migration(migrations.Migration):

    dependencies = [
        ("maintenance", "0003_backfill_maintenance_items"),
        ("generators",  "0003_replace_department_with_building"),
        ("vehicles",    "0003_drivervehicleassignment"),
    ]

    operations = [
        # Make vehicle nullable
        migrations.AlterField(
            model_name="maintenancerecord",
            name="vehicle",
            field=models.ForeignKey(
                blank=True, null=True,
                help_text="Set if this record is for a vehicle. Mutually exclusive with generator.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="maintenance_records",
                to="vehicles.vehicle",
            ),
        ),
        # Add generator FK
        migrations.AddField(
            model_name="maintenancerecord",
            name="generator",
            field=models.ForeignKey(
                blank=True, null=True,
                help_text="Set if this record is for a generator. Mutually exclusive with vehicle.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="maintenance_records",
                to="generators.generator",
            ),
        ),
        # Update service_type choices on both record and item
        migrations.AlterField(
            model_name="maintenancerecord",
            name="service_type",
            field=models.CharField(
                blank=True, max_length=20, choices=SERVICE_CHOICES,
                help_text="Primary service category. Auto-set from the first line item.",
            ),
        ),
        migrations.AlterField(
            model_name="maintenanceitem",
            name="service_type",
            field=models.CharField(max_length=20, choices=SERVICE_CHOICES),
        ),
        # Exactly one asset must be set
        migrations.AddConstraint(
            model_name="maintenancerecord",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(vehicle__isnull=False, generator__isnull=True)
                    | models.Q(vehicle__isnull=True, generator__isnull=False)
                ),
                name="maintenance_one_asset_only",
            ),
        ),
    ]
