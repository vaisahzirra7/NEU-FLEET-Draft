"""
Management command to send scheduled reports.

Run manually:
    python manage.py send_scheduled_reports

Or set up a daily cron job (runs at 6am every day):
    0 6 * * * cd /path/to/VanaraFleetOps && .venv/Scripts/python manage.py send_scheduled_reports
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import date, timedelta
from decimal import Decimal
import io
import os
import logging

logger = logging.getLogger(__name__)


def _email_wrapper(title, body_html, footer=""):
    """Wrap content in the branded email shell."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 16px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

        <!-- Header -->
        <tr>
          <td style="background:#0f2044;border-radius:16px 16px 0 0;padding:28px 36px;text-align:center;">
            <img src="cid:neu_logo" alt="NEU Logo"
              style="width:72px;height:72px;object-fit:contain;margin-bottom:14px;display:block;margin-left:auto;margin-right:auto;">
            <div style="font-size:20px;font-weight:700;color:#ffffff;letter-spacing:-.3px;">VanaraFleetsOps</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.45);margin-top:4px;">North-Eastern University, Gombe &nbsp;&middot;&nbsp; Fleet Management System</div>
          </td>
        </tr>

        <!-- Amber accent bar -->
        <tr><td style="background:#c8813a;height:4px;"></td></tr>

        <!-- Body -->
        <tr><td style="background:#fff;padding:36px 36px 28px;">
          {body_html}
        </td></tr>

        <!-- Footer -->
        <tr><td style="background:#f4f6fa;border-radius:0 0 16px 16px;padding:18px 36px;text-align:center;font-size:11px;color:#8a96b3;">
          {footer if footer else "This is an automated report from VanaraFleetsOps. Do not reply to this email."}
        </td></tr>

      </table>
    </td></tr>
  </table>
</body></html>"""


def _send(subject, html, recipients):
    """Send an HTML email to a list of recipients."""
    plain = "Please view this email in an HTML-capable email client."
    msg = EmailMultiAlternatives(
        subject=subject,
        body=plain,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "fleet@neu.edu.ng"),
        to=recipients,
    )
    msg.attach_alternative(html, "text/html")
    
    # Attach logo as CID inline image
    logo_path = getattr(settings, "REPORT_LOGO_PATH", None)
    if logo_path and os.path.exists(str(logo_path)):
        with open(str(logo_path), "rb") as f:
            logo_img = MIMEImage(f.read(), _subtype="png")
            logo_img.add_header("Content-ID", "<neu_logo>")
            logo_img.add_header("Content-Disposition", "inline", filename="neu_logo.png")
            msg.attach(logo_img)
    
    msg.send(fail_silently=True)
    


class Command(BaseCommand):
    help = "Send scheduled reports to configured recipients"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Send all active schedules regardless of send_day",
        )
        parser.add_argument(
            "--schedule-id",
            type=int,
            help="Only run a specific schedule by ID",
        )

    def handle(self, *args, **options):
        from reports.models import ReportSchedule

        today     = timezone.now().date()
        force     = options.get("force", False)
        sched_id  = options.get("schedule_id")

        qs = ReportSchedule.objects.filter(is_active=True)
        if sched_id:
            qs = qs.filter(pk=sched_id)

        sent = skipped = errors = 0

        for schedule in qs:
            if not force and schedule.send_day != today.day:
                self.stdout.write(f"  Skipping '{schedule.name}' — send day {schedule.send_day}, today is {today.day}")
                skipped += 1
                continue

            self.stdout.write(f"  Sending '{schedule.name}'...")
            try:
                attachment_data, attachment_name, mime_type = self._build_report(schedule, today)
                self._send_email(schedule, attachment_data, attachment_name, mime_type, today)
                schedule.last_sent = timezone.now()
                schedule.save(update_fields=["last_sent"])
                self.stdout.write(self.style.SUCCESS(f"  ✓ Sent '{schedule.name}' to {len(schedule.recipient_list)} recipient(s)"))
                sent += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ✗ Failed '{schedule.name}': {e}"))
                logger.exception(f"Failed to send scheduled report '{schedule.name}'")
                errors += 1

        self.stdout.write(f"\nDone — {sent} sent, {skipped} skipped, {errors} errors.")

    def _build_report(self, schedule, today):
        """Generate the report file and return (bytes, filename, mime_type)."""
        from reports.views import (
            _vehicle_spending_excel, _fleet_summary_excel,
            _monthly_expense_excel, _coupon_report_excel,
            _maintenance_excel, _vendor_excel,
        )
        from vehicles.models import Vehicle
        from drivers.models import Driver
        from coupons.models import FuelCoupon
        from fuel_logs.models import FuelLog
        from maintenance.models import MaintenanceRecord
        from vendors.models import Vendor
        from accounts.models import Department
        from django.db.models import Sum, Count, Q

        
        # Date range: previous full month
        first_of_this_month = today.replace(day=1)
        last_month_end      = first_of_this_month - timedelta(days=1)
        date_from           = last_month_end.replace(day=1)
        date_to             = last_month_end

        rt = schedule.report_type
        fmt = schedule.format

        if fmt == "xlsx":
            # Build Excel
            from django.http import HttpResponse
            if rt == "vehicle_spending":
                rows = self._vehicle_rows(date_from, date_to)
                gf   = sum(r["fuel_cost"] for r in rows)
                gm   = sum(r["maint_cost"] for r in rows)
                gt   = sum(r["total"] for r in rows)
                resp = _vehicle_spending_excel(rows, date_from, date_to, gf, gm, gt)
            elif rt == "fleet_summary":
                ctx  = self._fleet_summary_ctx(date_from, date_to)
                resp = _fleet_summary_excel(ctx)
            elif rt == "monthly_expense":
                ctx  = self._monthly_ctx(date_from, date_to)
                resp = _monthly_expense_excel(ctx)
            elif rt == "coupon_report":
                ctx  = self._coupon_ctx(date_from, date_to)
                resp = _coupon_report_excel(ctx)
            elif rt == "maintenance":
                ctx  = self._maint_ctx(date_from, date_to)
                resp = _maintenance_excel(ctx)
            elif rt == "vendor":
                ctx  = self._vendor_ctx(date_from, date_to)
                resp = _vendor_excel(ctx)
            else:
                raise ValueError(f"Unknown report type: {rt}")

            data     = b"".join(resp.streaming_content) if hasattr(resp, "streaming_content") else resp.content
            filename = f"{rt}_{date_from}_{date_to}.xlsx"
            mime     = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        else:
            # PDF — render the PDF view and capture output
            from django.test import RequestFactory
            from django.contrib.auth import get_user_model
            User = get_user_model()
            # Use first superuser for context (no real HTTP request needed for PDF)
            factory = RequestFactory()
            req = factory.get("/")
            req.user = User.objects.filter(is_system_admin=True).first() or User.objects.first()

            import importlib
            views_mod = importlib.import_module("reports.views")
            view_map  = {
                "vehicle_spending": "vehicle_spending",
                "fleet_summary":    "fleet_summary",
                "monthly_expense":  "monthly_expense",
                "coupon_report":    "coupon_report",
                "maintenance":      "maintenance_report",
                "vendor":           "vendor_report",
            }
            view_fn_name = view_map.get(rt)
            if not view_fn_name:
                raise ValueError(f"Unknown report type: {rt}")

            # For PDF we use weasyprint if available, otherwise skip and use xlsx
            try:
                import weasyprint
                view_fn = getattr(views_mod, view_fn_name)
                # Patch GET params
                req.GET = req.GET.copy()
                req.GET["date_from"] = str(date_from)
                req.GET["date_to"]   = str(date_to)
                req.GET["format"]    = "pdf"
                resp    = view_fn(req)
                html    = resp.content.decode("utf-8")
                pdf     = weasyprint.HTML(string=html, base_url=settings.BASE_DIR).write_pdf()
                data    = pdf
                filename = f"{rt}_{date_from}_{date_to}.pdf"
                mime     = "application/pdf"
            except ImportError:
                # weasyprint not installed — fallback to Excel
                self.stdout.write("  weasyprint not installed, falling back to Excel for PDF schedule")
                schedule.format = "xlsx"
                return self._build_report(schedule, today)

        return data, filename, mime

    ### Automated email sending helper for schedules — similar to the one in views.py but with a month label and no sent_by.
    def _send_email(self, schedule, data, filename, mime_type, today):
        month_label = today.replace(day=1) - timedelta(days=1)
        subject = (
            f"VanaraFleetsOps — {schedule.get_report_type_display()} "
            f"({month_label.strftime('%B %Y')})"
        )
        body = (
            f"Hello!\n\n"
            f"Please find attached the scheduled {schedule.get_report_type_display()} "
            f"report for {month_label.strftime('%B %Y')}.\n\n"
            f"This report was automatically generated and sent by VanaraFleetsOps.\n\n"
            f"Best regards,\n\n"
            f"— Fleet Management System\n"
            f"North-Eastern University, Gombe"
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "fleet@neu.edu.ng"),
            to=schedule.recipient_list,
        )
        msg.attach(filename, data, mime_type)
        msg.send()

    # ── Context builders (simplified — use all vehicles, no dept filter) ──

    def _vehicle_rows(self, df, dt):
        from vehicles.models import Vehicle
        from coupons.models import FuelCoupon
        from maintenance.models import MaintenanceRecord
        from django.db.models import Sum
        rows = []
        for v in Vehicle.objects.filter(status="active").select_related("department"):
            fuel_cost  = FuelCoupon.objects.filter(vehicle=v, status="redeemed", issue_datetime__date__range=[df, dt]).aggregate(t=Sum("total_value"))["t"] or Decimal(0)
            maint_cost = MaintenanceRecord.objects.filter(vehicle=v, service_date__range=[df, dt]).aggregate(t=Sum("total_cost"))["t"] or Decimal(0)
            fuel_litres= FuelCoupon.objects.filter(vehicle=v, status="redeemed", issue_datetime__date__range=[df, dt]).aggregate(t=Sum("litres"))["t"] or Decimal(0)
            maint_count= MaintenanceRecord.objects.filter(vehicle=v, service_date__range=[df, dt]).count()
            if fuel_cost or maint_cost:
                rows.append({"vehicle": v, "fuel_cost": fuel_cost, "maint_cost": maint_cost, "total": fuel_cost + maint_cost, "fuel_litres": fuel_litres, "maint_count": maint_count})
        return rows

    def _fleet_summary_ctx(self, df, dt):
        from coupons.models import FuelCoupon
        from maintenance.models import MaintenanceRecord
        from accounts.models import Department
        from django.db.models import Sum
        total_fuel   = FuelCoupon.objects.filter(status="redeemed", issue_datetime__date__range=[df,dt]).aggregate(t=Sum("total_value"))["t"] or Decimal(0)
        total_litres = FuelCoupon.objects.filter(status="redeemed", issue_datetime__date__range=[df,dt]).aggregate(t=Sum("litres"))["t"] or Decimal(0)
        total_maint  = MaintenanceRecord.objects.filter(service_date__range=[df,dt]).aggregate(t=Sum("total_cost"))["t"] or Decimal(0)
        dept_rows = []
        for dept in Department.objects.filter(is_active=True):
            f = FuelCoupon.objects.filter(vehicle__department=dept, status="redeemed", issue_datetime__date__range=[df,dt]).aggregate(t=Sum("total_value"))["t"] or Decimal(0)
            m = MaintenanceRecord.objects.filter(vehicle__department=dept, service_date__range=[df,dt]).aggregate(t=Sum("total_cost"))["t"] or Decimal(0)
            dept_rows.append({"dept": dept, "fuel": f, "maint": m, "total": f+m})
        return {
            "date_from": df, "date_to": dt,
            "total_fuel_cost": total_fuel, "total_fuel_litres": total_litres,
            "total_maint_cost": total_maint, "total_spend": total_fuel + total_maint,
            "total_coupons": FuelCoupon.objects.filter(issue_datetime__date__range=[df,dt]).count(),
            "total_maint_recs": MaintenanceRecord.objects.filter(service_date__range=[df,dt]).count(),
            "dept_rows": dept_rows,
        }

    def _monthly_ctx(self, df, dt):
        from fuel_logs.models import FuelLog
        from maintenance.models import MaintenanceRecord
        from django.db.models import Sum
        # select_related includes generator so PDF templates can render either
        # asset kind without a DB hit per row. Same for maintenance.
        logs  = FuelLog.objects.filter(fuel_date__range=[df,dt]).select_related("vehicle","driver","generator","coupon")
        recs  = MaintenanceRecord.objects.filter(service_date__range=[df,dt]).select_related("vehicle","generator","vendor").prefetch_related("items")
        return {
            "date_from": df, "date_to": dt,
            "fuel_logs": logs, "maint_records": recs,
            "total_fuel": logs.aggregate(t=Sum("actual_cost"))["t"] or Decimal(0),
            "total_maint": recs.aggregate(t=Sum("total_cost"))["t"] or Decimal(0),
        }

    def _coupon_ctx(self, df, dt):
        from coupons.models import FuelCoupon
        from django.db.models import Sum
        coupons = FuelCoupon.objects.filter(issue_datetime__date__range=[df,dt]).select_related("vehicle","driver","generator","fuel_station")
        return {
            "date_from": df, "date_to": dt,
            "coupons": coupons,
            "total_value": coupons.aggregate(t=Sum("total_value"))["t"] or Decimal(0),
        }

    def _maint_ctx(self, df, dt):
        from maintenance.models import MaintenanceRecord
        from django.db.models import Sum
        recs = MaintenanceRecord.objects.filter(service_date__range=[df,dt]).select_related("vehicle","generator","vendor").prefetch_related("items")
        return {
            "date_from": df, "date_to": dt,
            "records": recs,
            "total_cost": recs.aggregate(t=Sum("total_cost"))["t"] or Decimal(0),
        }

    def _vendor_ctx(self, df, dt):
        from vendors.models import Vendor
        from coupons.models import FuelCoupon
        from maintenance.models import MaintenanceRecord
        from django.db.models import Sum, Count
        from decimal import Decimal
        rows = []
        grand = Decimal(0)
        for v in Vendor.objects.filter(is_active=True):
            fc = FuelCoupon.objects.filter(fuel_station=v, issue_datetime__date__range=[df,dt])
            mc = MaintenanceRecord.objects.filter(vendor=v, service_date__range=[df,dt])
            fuel_cost   = fc.aggregate(t=Sum("total_value"))["t"] or Decimal(0)
            fuel_litres = fc.aggregate(t=Sum("litres"))["t"] or Decimal(0)
            maint_cost  = mc.aggregate(t=Sum("total_cost"))["t"] or Decimal(0)
            total       = fuel_cost + maint_cost
            if total:
                rows.append({"vendor": v, "fuel_cost": fuel_cost, "fuel_litres": fuel_litres, "fuel_txn": fc.count(), "maint_cost": maint_cost, "maint_txn": mc.count(), "total": total})
                grand += total
        return {"date_from": df, "date_to": dt, "rows": rows, "grand_total": grand}
