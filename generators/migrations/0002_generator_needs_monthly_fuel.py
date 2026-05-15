from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("generators", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="generator",
            name="needs_monthly_fuel",
            field=models.BooleanField(
                default=False,
                help_text="Flag generators that should receive fuel every month. Used for monthly-fuel reminders.",
            ),
        ),
    ]
