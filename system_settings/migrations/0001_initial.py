from django.db import migrations, models
import django.db.models.deletion
import system_settings.models


def seed_settings(apps, schema_editor):
    SystemSettings = apps.get_model("system_settings", "SystemSettings")
    SystemSettings.objects.get_or_create(
        pk=1,
        defaults={
            "system_name":          "VanaraFleetsOps",
            "institution_name":     "VanaraFleetsOps",
            "institution_subtitle": "North-Eastern University, Gombe  ·  FMS",
            "email_from":           "fleet@neu.edu.ng",
        },
    )


def add_settings_module(apps, schema_editor):
    """
    Grant the existing System Admin role full access to the new 'settings'
    module so the page is reachable on day one without manual permission setup.
    Other roles get no access by default — admins can grant later.
    """
    Role = apps.get_model("accounts", "Role")
    RoleModulePermission = apps.get_model("accounts", "RoleModulePermission")
    try:
        sysadmin = Role.objects.filter(is_system_admin=True).first()
    except Exception:
        sysadmin = None
    if sysadmin:
        RoleModulePermission.objects.get_or_create(
            role=sysadmin, module="settings",
            defaults={
                "can_read": True, "can_write": True,
                "can_edit": True, "can_delete": True,
            },
        )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0006_add_settings_module"),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("system_name", models.CharField(default="VanaraFleetsOps", help_text="Internal product name. Used in browser tab titles and email subjects.", max_length=120)),
                ("institution_name", models.CharField(default="VanaraFleetsOps", help_text="Big text shown next to the logo in the sidebar (e.g. 'VanaraFleetsOps').", max_length=160)),
                ("institution_subtitle", models.CharField(blank=True, default="North-Eastern University, Gombe  ·  FMS", help_text="Smaller line under the institution name (e.g. 'University of X · FMS').", max_length=200)),
                ("logo", models.ImageField(blank=True, help_text="Square or near-square logo for the sidebar. PNG/JPG/SVG. ~120x120 recommended.", null=True, upload_to=system_settings.models._logo_path)),
                ("favicon", models.ImageField(blank=True, help_text="Small icon shown in the browser tab. PNG or ICO. 32x32 or 64x64 recommended.", null=True, upload_to=system_settings.models._favicon_path)),
                ("email_from", models.EmailField(default="fleet@neu.edu.ng", help_text="From-address used for scheduled report emails and password resets.", max_length=200)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="+", to="accounts.user")),
            ],
            options={
                "verbose_name": "System Settings",
                "verbose_name_plural": "System Settings",
                "db_table": "system_settings",
            },
        ),
        migrations.RunPython(seed_settings, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(add_settings_module, reverse_code=migrations.RunPython.noop),
    ]
