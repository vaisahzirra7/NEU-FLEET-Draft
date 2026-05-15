from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_rolemodulepermission_can_approve_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rolemodulepermission",
            name="module",
            field=models.CharField(
                choices=[
                    ("vehicles",     "Vehicle Management"),
                    ("generators",   "Generator Management"),
                    ("drivers",      "Driver Management"),
                    ("coupons",      "Fuel Coupons"),
                    ("fuel_logs",    "Fuel Logs"),
                    ("maintenance",  "Maintenance"),
                    ("vendors",      "Vendor Register"),
                    ("reports",      "Reports"),
                    ("dashboard",    "Dashboard"),
                    ("users",        "User Management"),
                    ("roles",        "Role Management"),
                    ("audit",        "Audit Trail"),
                    ("trips",        "Trips"),
                    ("destinations", "Destinations"),
                ],
                max_length=50,
            ),
        ),
    ]
