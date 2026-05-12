from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ReportSchedule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("report_type", models.CharField(max_length=40, choices=[
                    ("fleet_summary", "Fleet Spending Summary"),
                    ("vehicle_spending", "Per-Vehicle Spending"),
                    ("monthly_expense", "Monthly Expense"),
                    ("coupon_report", "Fuel Coupon Report"),
                    ("maintenance", "Maintenance History"),
                    ("vendor", "Vendor Spend"),
                ])),
                ("format", models.CharField(max_length=10, choices=[("pdf", "PDF"), ("xlsx", "Excel")], default="pdf")),
                ("recipients", models.TextField()),
                ("send_day", models.PositiveSmallIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
                ("created_by", models.CharField(max_length=150)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("last_sent", models.DateTimeField(null=True, blank=True)),
            ],
            options={"db_table": "report_schedules", "ordering": ["name"]},
        ),
    ]
