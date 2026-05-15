from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("audit", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="auditlog",
            name="action",
            field=models.CharField(
                choices=[
                    ("create",          "Create"),
                    ("edit",            "Edit"),
                    ("delete",          "Delete"),
                    ("login",           "Login"),
                    ("logout",          "Logout"),
                    ("coupon_issue",    "Coupon Issued"),
                    ("coupon_redeem",   "Coupon Redeemed"),
                    ("coupon_cancel",   "Coupon Cancelled"),
                    ("coupon_approve",  "Coupon Approved"),
                    ("coupon_reject",   "Coupon Rejected"),
                ],
                max_length=20,
            ),
        ),
    ]
