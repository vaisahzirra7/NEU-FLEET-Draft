from django.db import migrations, models


REPORT_CHOICES = [
    ("vehicle_spending",   "Per-Vehicle Spending"),
    ("generator_spending", "Per-Generator Spending"),
    ("monthly_expense",    "Monthly Expense"),
    ("maintenance",        "Maintenance History"),
]


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0002_alter_reportschedule_id_alter_reportschedule_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reportschedule",
            name="report_type",
            field=models.CharField(max_length=40, choices=REPORT_CHOICES),
        ),
    ]
