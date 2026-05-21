from django.db import migrations, models


MODULE_CHOICES = [
    ("vehicles",       "Vehicle Management"),
    ("generators",     "Generator Management"),
    ("drivers",        "Driver Management"),
    ("coupons",        "Fuel Coupons"),
    ("fuel_logs",      "Fuel Logs"),
    ("maintenance",    "Maintenance"),
    ("vendors",        "Vendor Register"),
    ("reports",        "Reports"),
    ("dashboard",      "Dashboard"),
    ("users",          "User Management"),
    ("roles",          "Role Management"),
    ("audit",          "Audit Trail"),
    ("trips",          "Trips"),
    ("destinations",   "Destinations"),
    ("settings",       "System Settings"),
    ("settings_email", "SMTP / Email Settings"),
]


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_userinvite"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rolemodulepermission",
            name="module",
            field=models.CharField(max_length=50, choices=MODULE_CHOICES),
        ),
    ]
