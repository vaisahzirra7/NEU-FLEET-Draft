from django.db import models


class ReportSchedule(models.Model):
    """Stores scheduled report email deliveries."""

    REPORT_FLEET_SUMMARY  = "fleet_summary"
    REPORT_VEHICLE_SPEND  = "vehicle_spending"
    REPORT_MONTHLY_EXPENSE= "monthly_expense"
    REPORT_COUPON         = "coupon_report"
    REPORT_MAINTENANCE    = "maintenance"
    REPORT_VENDOR         = "vendor"

    REPORT_CHOICES = [
        (REPORT_VEHICLE_SPEND,   "Per-Vehicle Spending"),
        (REPORT_MONTHLY_EXPENSE, "Monthly Expense"),
        (REPORT_MAINTENANCE,     "Maintenance History"),
    ]

    FORMAT_PDF  = "pdf"
    FORMAT_XLSX = "xlsx"
    FORMAT_CHOICES = [
        (FORMAT_PDF,  "PDF"),
        (FORMAT_XLSX, "Excel"),
    ]

    name        = models.CharField(max_length=120, help_text="Friendly name for this schedule")
    report_type = models.CharField(max_length=40, choices=REPORT_CHOICES)
    format      = models.CharField(max_length=10, choices=FORMAT_CHOICES, default=FORMAT_PDF)
    recipients  = models.TextField(help_text="Comma-separated email addresses")
    send_day    = models.PositiveSmallIntegerField(
        default=1,
        help_text="Day of month to send (1-28). Use 1 for the 1st of each month."
    )
    is_active   = models.BooleanField(default=True)
    created_by  = models.CharField(max_length=150)
    created_at  = models.DateTimeField(auto_now_add=True)
    last_sent   = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "report_schedules"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} — day {self.send_day}"

    @property
    def recipient_list(self):
        return [e.strip() for e in self.recipients.split(",") if e.strip()]
