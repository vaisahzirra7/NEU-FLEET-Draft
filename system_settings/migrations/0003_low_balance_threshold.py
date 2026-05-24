from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("system_settings", "0002_smtp_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="systemsettings",
            name="low_balance_threshold",
            field=models.DecimalField(
                max_digits=14, decimal_places=2, default=0,
                help_text="A fuel station's available balance below this triggers a low-balance alert. Set to 0 to disable alerts.",
            ),
        ),
    ]
