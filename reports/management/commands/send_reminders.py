"""
Management command to send email reminders for:
  1. Driver licences expiring in 30 days (reminder)
  2. Driver licences that expired (alert)
  3. Fleet vehicle licence expiring in 60 days (reminder)
  4. Fleet vehicle licence that expired (alert)
  5. Monthly fuel reminders — notify coupon issuers when vehicles need fuel

Run daily via cron (recommended at 7am):
    0 7 * * * cd /path/to/VanaraFleetOps && .venv/Scripts/python manage.py send_reminders

# Commands for running specific reminder types
    Or run manually:
    python manage.py send_reminders
    python manage.py send_reminders --type driver_licence
    python manage.py send_reminders --type fleet_licence
    python manage.py send_reminders --type monthly_fuel
"""





from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import timedelta
from email.mime.image import MIMEImage
import os
import base64
import logging

logger = logging.getLogger(__name__)


def _logo_html():
    """Return an <img> tag with the NEU logo embedded as base64."""
    logo_path = getattr(settings, "REPORT_LOGO_PATH", None)
    if logo_path and os.path.exists(str(logo_path)):
        with open(str(logo_path), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (
            f"<img src='data:image/png;base64,{b64}' alt='NEU Logo' "
            f"style='width:56px;height:56px;object-fit:contain;"
            f"display:block;margin:0 auto 12px;'>"
        )
    return ""


def _email_wrapper(logo_html, title, body_html, footer=""):
    """Wrap content in the branded email shell."""
    return f"""<!DOCTYPE html>

    <html lang="en">


<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">

<title>{title}</title></head>

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
          {footer if footer else "This is an automated reminder from VanaraFleetsOps. Do not reply to this email."}
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


def _get_admin_emails():
    """Get emails of all active system admins."""
    from accounts.models import User
    return list(
        User.objects.filter(is_active=True, is_system_admin=True)
        .values_list("email", flat=True)
    )


def _get_coupon_issuer_emails():
    """Get emails of users who have coupons write permission."""
    from accounts.models import User, RoleModulePermission
    role_ids = RoleModulePermission.objects.filter(
        module="coupons", can_write=True
    ).values_list("role_id", flat=True)
    return list(
        User.objects.filter(is_active=True, role_id__in=role_ids)
        .values_list("email", flat=True)
    )



class Command(BaseCommand):
    help = "Send email reminders for licence expiry and monthly fuel"

    def add_arguments(self, parser):
        parser.add_argument(
            "--type",
            choices=["driver_licence", "fleet_licence", "monthly_fuel", "all"],
            default="all",
            help="Which reminder type to send",
        )

    def handle(self, *args, **options):
        reminder_type = options.get("type", "all")
        today  = timezone.now().date()
        logo   = _logo_html()
        admins = _get_admin_emails()

        if reminder_type in ("driver_licence", "all"):
            self._driver_licence_reminders(today, logo, admins)

        if reminder_type in ("fleet_licence", "all"):
            self._fleet_licence_reminder(today, logo, admins)

        if reminder_type in ("monthly_fuel", "all"):
            self._monthly_fuel_reminder(today, logo)

    
    
    # ── Driver Licence ────────────────────────────────────────────────────────

    def _driver_licence_reminders(self, today, logo, admins):
        from drivers.models import Driver

        if not admins:
            self.stdout.write("  No admin emails configured — skipping driver licence reminders.")
            return

        # --- Warning: expiring within 30 days ---
        warning_cutoff = today + timedelta(days=30)
        expiring = Driver.objects.filter(
            status=Driver.STATUS_ACTIVE,
            license_expiry__gt=today,
            license_expiry__lte=warning_cutoff,
        ).order_by("license_expiry")

        if expiring.exists():
            rows = "".join(
                f"""<tr style="border-bottom:1px solid #eee;">
                  <td style="padding:8px 12px;font-size:.85rem;font-weight:600;">{d.full_name}</td>
                  <td style="padding:8px 12px;font-size:.85rem;color:#5a6480;">{d.staff_id}</td>
                  <td style="padding:8px 12px;font-size:.85rem;">{d.license_no}</td>
                  <td style="padding:8px 12px;font-size:.85rem;font-weight:700;color:{'#c8813a' if d.days_until_license_expiry <= 7 else '#0f2044'};">
                    {d.license_expiry.strftime('%d %b %Y')}
                    <span style="font-size:.75rem;font-weight:400;color:#8a96b3;">({d.days_until_license_expiry}d left)</span>
                  </td>
                </tr>"""
                for d in expiring
            )
            body = f"""
              <p style="margin:0 0 8px;font-size:15px;font-weight:600;color:#0f2044;">Driver Licence Expiry Warning</p>
              
              <p style="margin:0 0 24px;font-size:14px;color:#5a6480;line-height:1.7;">
                The following {expiring.count()} active driver licence(s) are expiring within the next 30 days.
                Please arrange renewals as soon as possible.
              </p>
              
              <table width="100%" cellpadding="0" cellspacing="0"
                style="border-collapse:collapse;border:1px solid #dde2ed;border-radius:8px;overflow:hidden;font-family:'Segoe UI',Arial,sans-serif;">
                <thead>
                  <tr style="background:#0f2044;">
                    <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;font-weight:600;">Driver</th>
                    <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;font-weight:600;">Staff ID</th>
                    <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;font-weight:600;">Licence No.</th>
                    <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;font-weight:600;">Expiry Date</th>
                  </tr>
                </thead>
                <tbody>{rows}</tbody>
              </table>
              
              <p style="margin:20px 0 0;font-size:12px;color:#8a96b3;">
                Log in to VanaraFleetsOps to renew a licence: go to Drivers &rarr; Driver Detail &rarr; Renew Licence.
              </p>"""
            html = _email_wrapper(logo, "Driver Licence Expiry Warning", body)
            _send(
                f"VanaraFleetsOps — Driver Licence Expiry Warning ({expiring.count()} driver(s))",
                html, admins
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Driver licence WARNING sent — {expiring.count()} expiring soon"))

       
        
        
        # --- Alert: expired today ---
        expired_today = Driver.objects.filter(
            status=Driver.STATUS_ACTIVE,
            license_expiry=today,
        )
        if expired_today.exists():
            rows = "".join(
                f"""<tr style="border-bottom:1px solid #eee;">
                  <td style="padding:8px 12px;font-size:.85rem;font-weight:600;">{d.full_name}</td>
                  <td style="padding:8px 12px;font-size:.85rem;color:#5a6480;">{d.staff_id}</td>
                  <td style="padding:8px 12px;font-size:.85rem;">{d.license_no}</td>
                  <td style="padding:8px 12px;font-size:.85rem;font-weight:700;color:#c0392b;">EXPIRED TODAY</td>
                </tr>"""
                for d in expired_today
            )
            body = f"""
              <div style="background:#fdecea;border-left:4px solid #c0392b;border-radius:6px;padding:12px 16px;margin-bottom:20px;">
                <strong style="color:#c0392b;">Urgent:</strong>
                <span style="color:#5a6480;font-size:.88rem;"> The following driver licence(s) expired today and must be renewed immediately.</span>
              </div>
              <table width="100%" cellpadding="0" cellspacing="0"
                style="border-collapse:collapse;border:1px solid #dde2ed;border-radius:8px;overflow:hidden;">
                <thead>
                  <tr style="background:#c0392b;">
                    <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;">Driver</th>
                    <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;">Staff ID</th>
                    <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;">Licence No.</th>
                    <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;">Status</th>
                  </tr>
                </thead>
                <tbody>{rows}</tbody>
              </table>"""
            html = _email_wrapper(logo, "Driver Licence Expired", body)
            _send(
                f"VanaraFleetsOps — URGENT: Driver Licence Expired ({expired_today.count()} driver(s))",
                html, admins
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Driver licence EXPIRED alert sent — {expired_today.count()} expired today"))

    
    
    
    # ── Fleet Vehicle Licence ─────────────────────────────────────────────────

    def _fleet_licence_reminder(self, today, logo, admins):
        from vehicles.models import FleetLicenceExpiry

        fleet = FleetLicenceExpiry.get()
        if not fleet or not admins:
            return

        days_left = fleet.days_until_expiry

        # Warning: within 60 days
        if 0 < days_left <= 60:
            body = f"""
              <p style="margin:0 0 8px;font-size:15px;font-weight:600;color:#0f2044;">Fleet Vehicle Licence Expiry Warning</p>
              <p style="margin:0 0 20px;font-size:14px;color:#5a6480;line-height:1.7;">
                The fleet vehicle licences for North-Eastern University, Gombe are due to expire in
                <strong style="color:#c8813a;">{days_left} day(s)</strong>.
              </p>
              <table width="100%" cellpadding="0" cellspacing="0"
                style="border-collapse:collapse;background:#f4f6fa;border-radius:8px;overflow:hidden;">
                <tr>
                  <td style="padding:16px 20px;font-size:.85rem;color:#5a6480;width:50%;">Expiry Date</td>
                  <td style="padding:16px 20px;font-size:.95rem;font-weight:700;color:#c8813a;">{fleet.expiry_date.strftime('%d %B %Y')}</td>
                </tr>
                <tr style="border-top:1px solid #dde2ed;">
                  <td style="padding:16px 20px;font-size:.85rem;color:#5a6480;">Days Remaining</td>
                  <td style="padding:16px 20px;font-size:.95rem;font-weight:700;color:#c8813a;">{days_left} day(s)</td>
                </tr>
                {'<tr style="border-top:1px solid #dde2ed;"><td style="padding:16px 20px;font-size:.85rem;color:#5a6480;">Notes</td><td style="padding:16px 20px;font-size:.85rem;color:#5a6480;">' + fleet.notes + '</td></tr>' if fleet.notes else ''}
              </table>
              <p style="margin:20px 0 0;font-size:12px;color:#8a96b3;">
                Log in to VanaraFleetsOps and update the fleet licence expiry date once renewed.
              </p>"""
            html = _email_wrapper(logo, "Fleet Licence Expiry Warning", body)
            _send(
                f"VanaraFleetsOps — Fleet Vehicle Licence Expiring in {days_left} Day(s)",
                html, admins
            )
            self.stdout.write(self.style.SUCCESS(f"  ✓ Fleet licence WARNING sent — {days_left} days left"))

        
        
        # Alert: expired today
        elif days_left == 0 or fleet.is_expired:
            body = f"""
              <div style="background:#fdecea;border-left:4px solid #c0392b;border-radius:6px;padding:12px 16px;margin-bottom:20px;">
                <strong style="color:#c0392b;">Urgent:</strong>
                <span style="color:#5a6480;font-size:.88rem;"> The fleet vehicle licences have expired. Immediate action is required.</span>
              </div>
              <table width="100%" cellpadding="0" cellspacing="0"
                style="border-collapse:collapse;background:#f4f6fa;border-radius:8px;overflow:hidden;">
                <tr>
                  <td style="padding:16px 20px;font-size:.85rem;color:#5a6480;">Expiry Date</td>
                  <td style="padding:16px 20px;font-size:.95rem;font-weight:700;color:#c0392b;">{fleet.expiry_date.strftime('%d %B %Y')} — EXPIRED</td>
                </tr>
              </table>
              <p style="margin:20px 0 0;font-size:12px;color:#8a96b3;">
                Renew the fleet licences immediately and update the expiry date in VanaraFleetsOps.
              </p>"""
            html = _email_wrapper(logo, "Fleet Vehicle Licence Expired", body)
            _send(
                "VanaraFleetsOps — URGENT: Fleet Vehicle Licences Have Expired",
                html, admins
            )
            self.stdout.write(self.style.SUCCESS("  ✓ Fleet licence EXPIRED alert sent"))

    
    
    # ── Monthly Fuel Reminder ─────────────────────────────────────────────────

    def _monthly_fuel_reminder(self, today, logo):
        from vehicles.models import Vehicle, MonthlyFuelDismissal

        # Only send on the 1st of the month (or if forced)
        dismissed_ids = MonthlyFuelDismissal.objects.filter(
            month=today.month, year=today.year
        ).values_list("vehicle_id", flat=True)

        pending = Vehicle.objects.filter(
            needs_monthly_fuel=True, status=Vehicle.STATUS_ACTIVE
        ).exclude(id__in=dismissed_ids).select_related("department", "default_driver")

        if not pending.exists():
            self.stdout.write("  No pending monthly fuel vehicles — skipping.")
            return

        recipients = _get_coupon_issuer_emails()
        if not recipients:
            self.stdout.write("  No coupon issuer emails found — skipping monthly fuel reminder.")
            return

        rows = "".join(
            f"""<tr style="border-bottom:1px solid #eee;">
              <td style="padding:8px 12px;font-size:.85rem;font-weight:600;">{v.plate_number}</td>
              <td style="padding:8px 12px;font-size:.85rem;color:#5a6480;">{v.make} {v.model}</td>
              <td style="padding:8px 12px;font-size:.85rem;color:#5a6480;">{v.department.name}</td>
              <td style="padding:8px 12px;font-size:.85rem;">{v.default_driver.full_name if v.default_driver else '—'}</td>
            </tr>"""
            for v in pending
        )

        body = f"""
          <p style="margin:0 0 8px;font-size:15px;font-weight:600;color:#0f2044;">Monthly Fuel Reminder</p>
          <p style="margin:0 0 20px;font-size:14px;color:#5a6480;line-height:1.7;">
            The following <strong>{pending.count()} vehicle(s)</strong> are due for their monthly fuel allocation
            for <strong style="color:#0f2044;">{today.strftime('%B %Y')}</strong> and have not yet received a coupon.
            Please log in and issue their fuel coupons.
          </p>
          <table width="100%" cellpadding="0" cellspacing="0"
            style="border-collapse:collapse;border:1px solid #dde2ed;border-radius:8px;overflow:hidden;">
            <thead>
              <tr style="background:#0f2044;">
                <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;">Plate No.</th>
                <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;">Vehicle</th>
                <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;">Department</th>
                <th style="padding:10px 12px;text-align:left;font-size:.78rem;color:#fff;">Default Driver</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
          <div style="margin-top:24px;text-align:center;">
            <a href="http://127.0.0.1:8000/coupons/issue/bulk/"
              style="display:inline-block;background:#0f2044;color:#fff;padding:10px 28px;border-radius:8px;font-size:.88rem;font-weight:600;text-decoration:none;">
              Issue Fuel Coupons &rarr;
            </a>
          </div>
          <p style="margin:16px 0 0;font-size:12px;color:#8a96b3;text-align:center;">
            Once coupons are issued, the reminder will automatically disappear from your dashboard.
          </p>"""

        html = _email_wrapper(logo, "Monthly Fuel Reminder", body)
        _send(
            f"VanaraFleetsOps — Monthly Fuel Reminder: {pending.count()} Vehicle(s) Pending ({today.strftime('%B %Y')})",
            html, recipients
        )
        self.stdout.write(self.style.SUCCESS(f"  ✓ Monthly fuel reminder sent to {len(recipients)} user(s) — {pending.count()} vehicles pending"))
