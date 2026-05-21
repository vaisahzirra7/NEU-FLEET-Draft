from django.db import migrations, models


def grant_settings_email_to_admin(apps, schema_editor):
    """
    Grant the existing System Admin role full access to the new 'settings_email'
    module so they can manage SMTP from day one. Other roles get nothing.
    """
    Role = apps.get_model("accounts", "Role")
    RoleModulePermission = apps.get_model("accounts", "RoleModulePermission")
    try:
        sysadmin = Role.objects.filter(is_system_admin=True).first()
    except Exception:
        sysadmin = None
    if sysadmin:
        RoleModulePermission.objects.get_or_create(
            role=sysadmin, module="settings_email",
            defaults={
                "can_read": True, "can_write": True,
                "can_edit": True, "can_delete": True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("system_settings", "0001_initial"),
        ("accounts", "0008_add_settings_email_module"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemsettings",
            name="smtp_host",
            field=models.CharField(
                blank=True, default="", max_length=200,
                help_text="SMTP server hostname (e.g. smtp.zoho.com). Leave blank to use settings.py.",
            ),
        ),
        migrations.AddField(
            model_name="systemsettings",
            name="smtp_port",
            field=models.PositiveIntegerField(
                null=True, blank=True,
                help_text="SMTP server port. Typical: 587 (TLS), 465 (SSL), 25 (legacy).",
            ),
        ),
        migrations.AddField(
            model_name="systemsettings",
            name="smtp_user",
            field=models.CharField(
                blank=True, default="", max_length=200,
                help_text="SMTP login username (usually an email address).",
            ),
        ),
        migrations.AddField(
            model_name="systemsettings",
            name="smtp_password_encrypted",
            field=models.TextField(
                blank=True, default="",
                help_text="SMTP password stored encrypted. NEVER displayed in the UI.",
            ),
        ),
        migrations.AddField(
            model_name="systemsettings",
            name="smtp_use_tls",
            field=models.BooleanField(
                default=True,
                help_text="Use STARTTLS (port 587). Mutually exclusive with SSL.",
            ),
        ),
        migrations.AddField(
            model_name="systemsettings",
            name="smtp_use_ssl",
            field=models.BooleanField(
                default=False,
                help_text="Use direct SSL/TLS on connect (port 465). Mutually exclusive with TLS.",
            ),
        ),
        migrations.RunPython(
            grant_settings_email_to_admin,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
