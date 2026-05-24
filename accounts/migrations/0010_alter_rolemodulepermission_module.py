from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Reflect the MODULE_CHOICES additions in the database column definition.
    This is what Django's `makemigrations` produces when the `choices=` on
    a CharField changes. Required so the migration graph stays consistent
    between local and production.
    """

    dependencies = [
        ("accounts", "0009_add_station_deposits_module"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rolemodulepermission",
            name="module",
            field=models.CharField(
                choices=[
                    ("vehicles",        "Vehicle Management"),
                    ("generators",      "Generator Management"),
                    ("drivers",         "Driver Management"),
                    ("coupons",         "Fuel Coupons"),
                    ("fuel_logs",       "Fuel Logs"),
                    ("maintenance",     "Maintenance"),
                    ("vendors",         "Vendor Register"),
                    ("station_deposits","Fuel Station Deposits"),
                    ("reports",         "Reports"),
                    ("report_schedules","Report Schedules"),
                    ("dashboard",       "Dashboard"),
                    ("users",           "User Management"),
                    ("roles",           "Role Management"),
                    ("departments",     "Departments"),
                    ("audit",           "Audit Trail"),
                    ("trips",           "Trips"),
                    ("destinations",    "Destinations"),
                    ("settings",        "System Settings"),
                    ("settings_email",  "SMTP / Email Settings"),
                ],
                max_length=50,
            ),
        ),
    ]
