from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0009_add_station_deposits_module"),
        ("vendors", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StationDeposit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(
                    decimal_places=2, max_digits=14,
                    help_text="Amount deposited. Must be a positive number.")),
                ("deposit_date", models.DateField(
                    help_text="The date the deposit was made at the bank / station.")),
                ("reference_number", models.CharField(
                    blank=True, default="", max_length=80,
                    help_text="Bank reference, transfer slip number, teller ID, etc. Optional but recommended.")),
                ("note", models.TextField(
                    blank=True, default="",
                    help_text="Optional note: source of funds, purpose, context.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("created_by", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="deposits_made",
                    to="accounts.user",
                    help_text="The admin who recorded this deposit.")),
                ("vendor", models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name="deposits",
                    limit_choices_to={"type": "fuel_station"},
                    to="vendors.vendor",
                    help_text="The fuel station receiving this deposit.")),
            ],
            options={
                "db_table": "station_deposits",
                "ordering": ["-deposit_date", "-created_at"],
                "indexes": [
                    models.Index(fields=["vendor", "-deposit_date"], name="station_dep_vendor_d_idx"),
                ],
            },
        ),
    ]
