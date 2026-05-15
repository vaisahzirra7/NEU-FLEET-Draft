from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("coupons", "0004_fuelcoupon_approved_at_fuelcoupon_approved_by_and_more"),
        ("generators", "0003_replace_department_with_building"),
        ("vehicles", "0003_drivervehicleassignment"),
        ("drivers", "0003_driver_payment_type"),
    ]

    operations = [
        # Make vehicle nullable
        migrations.AlterField(
            model_name="fuelcoupon",
            name="vehicle",
            field=models.ForeignKey(
                blank=True, null=True,
                help_text="Set if this coupon is for a vehicle. Mutually exclusive with generator.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="coupons", to="vehicles.vehicle",
            ),
        ),
        # Make driver nullable
        migrations.AlterField(
            model_name="fuelcoupon",
            name="driver",
            field=models.ForeignKey(
                blank=True, null=True,
                help_text="Driver who will collect the fuel. Required for vehicle coupons; null for generator coupons.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="coupons", to="drivers.driver",
            ),
        ),
        # Add generator FK
        migrations.AddField(
            model_name="fuelcoupon",
            name="generator",
            field=models.ForeignKey(
                blank=True, null=True,
                help_text="Set if this coupon is for a generator. Mutually exclusive with vehicle.",
                on_delete=django.db.models.deletion.PROTECT,
                related_name="coupons", to="generators.generator",
            ),
        ),
        # Enforce exactly one asset
        migrations.AddConstraint(
            model_name="fuelcoupon",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(vehicle__isnull=False, generator__isnull=True)
                    | models.Q(vehicle__isnull=True, generator__isnull=False)
                ),
                name="coupon_one_asset_only",
            ),
        ),
        # Driver only valid when vehicle is set
        migrations.AddConstraint(
            model_name="fuelcoupon",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(vehicle__isnull=False)
                    | models.Q(driver__isnull=True)
                ),
                name="coupon_driver_only_with_vehicle",
            ),
        ),
    ]
