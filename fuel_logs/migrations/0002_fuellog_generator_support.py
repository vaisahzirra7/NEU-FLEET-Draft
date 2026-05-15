from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fuel_logs", "0001_initial"),
        ("coupons", "0005_coupon_generator_support"),
        ("generators", "0003_replace_department_with_building"),
        ("vehicles", "0003_drivervehicleassignment"),
        ("drivers", "0003_driver_payment_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fuellog",
            name="vehicle",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fuel_logs", to="vehicles.vehicle",
            ),
        ),
        migrations.AlterField(
            model_name="fuellog",
            name="driver",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fuel_logs", to="drivers.driver",
            ),
        ),
        migrations.AddField(
            model_name="fuellog",
            name="generator",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="fuel_logs", to="generators.generator",
            ),
        ),
        migrations.AddConstraint(
            model_name="fuellog",
            constraint=models.CheckConstraint(
                check=(
                    models.Q(vehicle__isnull=False, generator__isnull=True)
                    | models.Q(vehicle__isnull=True, generator__isnull=False)
                ),
                name="fuellog_one_asset_only",
            ),
        ),
    ]
