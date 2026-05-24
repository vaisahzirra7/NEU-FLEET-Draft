from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("coupons", "0005_coupon_generator_support"),
    ]

    operations = [
        migrations.AddField(
            model_name="fuelcoupon",
            name="issued_with_override",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "True if this coupon was issued despite the fuel station having "
                    "insufficient available balance, via Super Admin override. "
                    "Surfaced in audit and reports."
                ),
            ),
        ),
    ]
