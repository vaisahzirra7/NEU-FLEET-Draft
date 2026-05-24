from django.db import migrations, models


MODULE_CHOICES = [
    ("vehicles",         "Vehicle Management"),
    ("generators",       "Generator Management"),
    ("drivers",          "Driver Management"),
    ("coupons",          "Fuel Coupons"),
    ("fuel_logs",        "Fuel Logs"),
    ("maintenance",      "Maintenance"),
    ("vendors",          "Vendor Register"),
    ("reports",          "Reports"),
    ("dashboard",        "Dashboard"),
    ("users",            "User Management"),
    ("roles",            "Role Management"),
    ("audit",            "Audit Trail"),
    ("trips",            "Trips"),
    ("destinations",     "Destinations"),
    ("settings",         "System Settings"),
    ("settings_email",   "SMTP / Email Settings"),
    ("station_deposits", "Fuel Station Deposits"),
]


def grant_station_deposits_to_admin(apps, schema_editor):
    Role = apps.get_model("accounts", "Role")
    RoleModulePermission = apps.get_model("accounts", "RoleModulePermission")
    sysadmin = Role.objects.filter(is_system_role=True, name__iexact="super admin").first()
    if not sysadmin:
        sysadmin = Role.objects.filter(is_system_role=True).first()
    if sysadmin:
        RoleModulePermission.objects.get_or_create(
            role=sysadmin, module="station_deposits",
            defaults={"can_read": True, "can_write": True, "can_edit": False, "can_delete": True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_add_settings_email_module"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rolemodulepermission",
            name="module",
            field=models.CharField(max_length=50, choices=MODULE_CHOICES),
        ),
        migrations.RunPython(grant_station_deposits_to_admin, reverse_code=migrations.RunPython.noop),
    ]
