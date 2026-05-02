from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import date, timedelta
from decimal import Decimal
import io
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage
from django.conf import settings

from coupons.models import FuelCoupon
from fuel_logs.models import FuelLog
from maintenance.models import MaintenanceRecord
from vehicles.models import Vehicle
from drivers.models import Driver
from vendors.models import Vendor
from audit.models import AuditLog
from accounts.models import Department


# ── Helpers ────────────────────────────────────────────────────────────

def dept_q(user, prefix=""):
    """Return department filter dict for a given queryset prefix."""
    p = f"{prefix}__" if prefix else ""
    if user.is_system_admin or not user.department:
        return {}
    return {f"{p}department": user.department} if prefix else {"department": user.department}


def parse_dates(request):
    """Parse date_from / date_to from request GET, default to current month."""
    today = date.today()
    date_from_str = request.GET.get("date_from", "")
    date_to_str   = request.GET.get("date_to", "")
    try:
        date_from = date.fromisoformat(date_from_str) if date_from_str else today.replace(day=1)
    except ValueError:
        date_from = today.replace(day=1)
    try:
        date_to = date.fromisoformat(date_to_str) if date_to_str else today
    except ValueError:
        date_to = today
    return date_from, date_to


# ── Excel helpers ───────────────────────────────────────────────────────

# Colour palette (matches PDF brown/navy theme)
NAVY   = "0F2044"
NAVY2  = "1A3260"
BROWN  = "6B2D0F"
BROWN2 = "8B3D15"
GOLD   = "C8813A"
GOLD2  = "D99850"
LIGHT  = "F4F6FA"
STRIPE = "EEF1F8"
WHITE  = "FFFFFF"
MUTED  = "6B7A99"


def xl_workbook(title):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = title
    ws.sheet_view.showGridLines = False
    return wb, ws


def _get_logo_image(target_height_px=68):
    """Load the university logo, resize proportionally, return XLImage + dimensions."""
    try:
        logo_path = getattr(settings, "REPORT_LOGO_PATH", None)
        if not logo_path or not os.path.exists(str(logo_path)):
            return None, 0, 0
        pil_img = PILImage.open(str(logo_path)).convert("RGBA")
        orig_w, orig_h = pil_img.size
        ratio = target_height_px / orig_h
        new_w = int(orig_w * ratio)
        pil_img = pil_img.resize((new_w, target_height_px), PILImage.LANCZOS)
        buf = io.BytesIO()
        pil_img.save(buf, format="PNG")
        buf.seek(0)
        xl_img = XLImage(buf)
        xl_img.width  = new_w
        xl_img.height = target_height_px
        return xl_img, new_w, target_height_px
    except Exception:
        return None, 0, 0


def xl_title_block(ws, title, subtitle, date_from, date_to, n_cols=8):
    """
    Header block matching exact user specification:
      Row 1  — navy, empty  (36pt) — logo anchored here, centred
      Row 2  — navy, institution name centred (36pt)
      Row 3  — navy, empty  (18pt) — bottom padding for logo
      Row 4  — brown, report title (26pt)
      Row 5  — light, meta info (16pt)
      Row 6  — spacer (6pt)
      Row 7  — column headers
      Row 8+ — data
    """
    from openpyxl.drawing.spreadsheet_drawing import OneCellAnchor, AnchorMarker
    from openpyxl.utils.units import pixels_to_EMU
    import openpyxl.utils as _utils

    last_col = _utils.get_column_letter(n_cols)
    navy_fill  = PatternFill("solid", fgColor=NAVY)
    brown_fill = PatternFill("solid", fgColor=BROWN)
    light_fill = PatternFill("solid", fgColor=LIGHT)

    # ── Rows 1-3: Navy banner ──
    row_heights = {1: 36.0, 2: 36.0, 3: 18.0}
    for r in (1, 2, 3):
        ws.merge_cells(f"A{r}:{last_col}{r}")
        ws.cell(r, 1).fill = navy_fill
        ws.row_dimensions[r].height = row_heights[r]

    # Institution name in row 2, centred
    c = ws.cell(2, 1)
    c.value     = "NORTH-EASTERN UNIVERSITY, GOMBE  •  FLEET MANAGEMENT SYSTEM"
    c.font      = Font(bold=True, size=12, color=WHITE, name="Calibri")
    c.alignment = Alignment(horizontal="center", vertical="center")

    # ── Logo: centred over rows 1-3 ──
    # Total banner height in px: rows 1+2+3 = 36+36+18 = 90pt → ~90*1.333 = 120px
    # Logo height = 68px leaves ~26px padding top+bottom
    logo, logo_w, logo_h = _get_logo_image(target_height_px=68)
    if logo:
        # Approximate total sheet width in pixels (col width units * 7px/unit)
        col_widths_px = []
        for ci in range(1, n_cols + 1):
            col_letter = _utils.get_column_letter(ci)
            w = ws.column_dimensions[col_letter].width or 8
            col_widths_px.append(w * 7)
        total_w_px = sum(col_widths_px)

        # Centre the logo horizontally
        left_px = max(0, (total_w_px - logo_w) // 2)
        # Small top padding inside row 1
        top_px  = 8

        left_emu = pixels_to_EMU(int(left_px))
        top_emu  = pixels_to_EMU(int(top_px))

        marker = AnchorMarker(col=0, colOff=left_emu, row=0, rowOff=top_emu)
        logo.anchor = OneCellAnchor(_from=marker, ext=None)
        logo.anchor.ext.cx = pixels_to_EMU(logo_w)
        logo.anchor.ext.cy = pixels_to_EMU(logo_h)
        ws.add_image(logo)

    # ── Row 4: Brown — report title ──
    ws.merge_cells(f"A4:{last_col}4")
    c = ws.cell(4, 1)
    c.value     = title.upper()
    c.font      = Font(bold=True, size=14, color=WHITE, name="Calibri")
    c.fill      = brown_fill
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[4].height = 25.95

    # ── Row 5: Meta bar ──
    ws.merge_cells(f"A5:{last_col}5")
    period = f"{date_from.strftime('%d %b %Y')} — {date_to.strftime('%d %b %Y')}"
    meta   = f"Period: {period}"
    if subtitle:
        meta = f"{subtitle}   |   {meta}"
    meta += "   |   Confidential — For Internal Use Only"
    c = ws.cell(5, 1)
    c.value     = meta
    c.font      = Font(italic=True, size=9, color=MUTED, name="Calibri")
    c.fill      = light_fill
    c.alignment = Alignment(horizontal="center", vertical="center")
    c.border    = Border(bottom=Side(style="thin", color=GOLD))
    ws.row_dimensions[5].height = 16.05

    # ── Row 6: Spacer ──
    ws.row_dimensions[6].height = 6.0


def xl_header_row(ws, cols, row=7):
    """Column header row — navy fill, white bold text, centred."""
    navy_fill  = PatternFill("solid", fgColor=NAVY2)
    white_font = Font(color=WHITE, bold=True, size=10, name="Calibri")
    center     = Alignment(horizontal="center", vertical="center", wrap_text=True)
    border     = Border(
        bottom=Side(style="medium", color=GOLD),
        top=Side(style="thin", color=NAVY),
    )
    for col_idx, label in enumerate(cols, 1):
        cell = ws.cell(row=row, column=col_idx, value=label)
        cell.fill      = navy_fill
        cell.font      = white_font
        cell.alignment = center
        cell.border    = border
    ws.row_dimensions[row].height = 24
    # Freeze panes so header + title stays visible when scrolling
    ws.freeze_panes = ws.cell(row=row + 1, column=1)


def xl_data_row(ws, values, row, shade=False):
    """Data row with alternating stripe, bottom border, and number formatting."""
    fill   = PatternFill("solid", fgColor=STRIPE) if shade else PatternFill("solid", fgColor=WHITE)
    border = Border(bottom=Side(style="thin", color="DDDDDD"))
    for col_idx, val in enumerate(values, 1):
        cell = ws.cell(row=row, column=col_idx, value=val)
        cell.fill      = fill
        cell.border    = border
        cell.font      = Font(size=10, name="Calibri")
        cell.alignment = Alignment(vertical="center", indent=1)
        if isinstance(val, (int, float, Decimal)):
            cell.number_format = '#,##0.00' if isinstance(val, (float, Decimal)) else '#,##0'
            cell.alignment = Alignment(horizontal="right", vertical="center")
    ws.row_dimensions[row].height = 18


def xl_totals_row(ws, row, n_cols, label_col=1, value_cols=None, values=None):
    """
    Write a gold-accented totals row.
    value_cols — list of 1-based column indices that get a value
    values     — matching list of values
    """
    gold_fill  = PatternFill("solid", fgColor=GOLD)
    navy_font  = Font(bold=True, size=10, color=NAVY, name="Calibri")
    border     = Border(
        top=Side(style="medium", color=BROWN),
        bottom=Side(style="thin", color=BROWN2),
    )
    for col_idx in range(1, n_cols + 1):
        cell = ws.cell(row=row, column=col_idx)
        cell.fill   = gold_fill
        cell.border = border
        cell.font   = navy_font
        cell.alignment = Alignment(vertical="center", indent=1)

    ws.cell(row=row, column=label_col).value = "GRAND TOTAL"

    if value_cols and values:
        for col_idx, val in zip(value_cols, values):
            cell = ws.cell(row=row, column=col_idx, value=val)
            cell.number_format = '#,##0.00'
            cell.alignment = Alignment(horizontal="right", vertical="center")
    ws.row_dimensions[row].height = 22


def xl_response(wb, filename):
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response


# ── PDF helper ──────────────────────────────────────────────────────────

def pdf_response(html_string, filename):
    # Serve as HTML — browser prints/saves as PDF with full CSS support
    response = HttpResponse(html_string, content_type="text/html; charset=utf-8")
    return response


# ── Dashboard ───────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    user  = request.user
    today = date.today()

    vdept = dept_q(user)
    fdept = dept_q(user, "vehicle")

    coupons_today = FuelCoupon.objects.filter(
        issue_datetime__date=today, **fdept
    ).count()
    coupon_value_today = FuelCoupon.objects.filter(
        issue_datetime__date=today, **fdept
    ).aggregate(t=Sum("total_value"))["t"] or 0
    open_coupons = FuelCoupon.objects.filter(
        status=FuelCoupon.STATUS_ISSUED, **fdept
    ).count()

    month_start = today.replace(day=1)
    fuel_spend  = FuelLog.objects.filter(fuel_date__gte=month_start, **fdept).aggregate(t=Sum("actual_cost"))["t"] or 0
    maint_spend = MaintenanceRecord.objects.filter(service_date__gte=month_start, **fdept).aggregate(t=Sum("total_cost"))["t"] or 0
    monthly_spend = fuel_spend + maint_spend

    active_vehicles = Vehicle.objects.filter(status=Vehicle.STATUS_ACTIVE, **vdept).count()
    total_vehicles  = Vehicle.objects.filter(**vdept).count()

    stats = {
        "coupons_today": coupons_today,
        "coupon_value_today": coupon_value_today,
        "open_coupons": open_coupons,
        "monthly_spend": monthly_spend,
        "active_vehicles": active_vehicles,
        "total_vehicles": total_vehicles,
    }

    alerts = []
    cutoff = today + timedelta(days=14)
    service_due_qs = MaintenanceRecord.objects.filter(
        next_service_date__lte=cutoff, next_service_date__gte=today, **fdept
    ).select_related("vehicle").order_by("next_service_date")

    seen = set()
    service_due = []
    for rec in service_due_qs:
        if rec.vehicle_id not in seen:
            seen.add(rec.vehicle_id)
            service_due.append(rec)
            alerts.append({
                "type": "warning",
                "title": f"Service due: {rec.vehicle.plate_number}",
                "detail": f"{rec.vehicle.make} {rec.vehicle.model} — due {rec.next_service_date}",
                "url": f"/vehicles/{rec.vehicle.pk}/",
            })

    license_cutoff = today + timedelta(days=30)
    license_alerts = Driver.objects.filter(
        status=Driver.STATUS_ACTIVE,
        license_expiry__lte=license_cutoff,
    ).order_by("license_expiry")
    for d in license_alerts:
        alerts.append({
            "type": "danger",
            "title": f"License expiring: {d.full_name}",
            "detail": f"Expires {d.license_expiry} ({d.days_until_license_expiry} days left)",
            "url": f"/drivers/{d.pk}/",
        })

    fuel_map  = {r["vehicle_id"]: r["fuel"]  for r in FuelLog.objects.filter(fuel_date__gte=month_start, **fdept).values("vehicle_id").annotate(fuel=Sum("actual_cost"))}
    maint_map = {r["vehicle_id"]: r["maint"] for r in MaintenanceRecord.objects.filter(service_date__gte=month_start, **fdept).values("vehicle_id").annotate(maint=Sum("total_cost"))}
    all_ids   = set(fuel_map) | set(maint_map)
    top_raw   = sorted([{"vehicle_id": v, "total_cost": (fuel_map.get(v) or 0) + (maint_map.get(v) or 0)} for v in all_ids], key=lambda x: x["total_cost"], reverse=True)
    vehicles_map = {v.pk: v for v in Vehicle.objects.filter(pk__in=[r["vehicle_id"] for r in top_raw[:5]])}
    top_vehicles = []
    for r in top_raw[:5]:
        v = vehicles_map.get(r["vehicle_id"])
        if v:
            v.total_cost = r["total_cost"]
            top_vehicles.append(v)

    recent_activity = AuditLog.objects.select_related("user")[:10]

    return render(request, "dashboard/dashboard.html", {
        "stats": stats,
        "alerts": alerts,
        "service_due": service_due,
        "license_alerts": license_alerts,
        "top_vehicles": top_vehicles,
        "recent_activity": recent_activity,
        # Permission flags for dynamic dashboard
        "can_see_coupons":     request.user.has_module_perm("coupons", "read"),
        "can_see_fuel_logs":   request.user.has_module_perm("fuel_logs", "read"),
        "can_see_maintenance": request.user.has_module_perm("maintenance", "read"),
        "can_see_vehicles":    request.user.has_module_perm("vehicles", "read"),
        "can_see_drivers":     request.user.has_module_perm("drivers", "read"),
        "can_see_reports":     request.user.has_module_perm("reports", "read"),
        "can_see_audit":       request.user.has_module_perm("audit", "read"),
    })


# ── Reports Index ────────────────────────────────────────────────────────

@login_required
def reports_index(request):
    if not request.user.has_module_perm("reports", "read"):
        return HttpResponseForbidden()
    return render(request, "reports/index.html")


# ═══════════════════════════════════════════════════════════════════════
# REPORT 1 — Per-Vehicle Spending
# ═══════════════════════════════════════════════════════════════════════

@login_required
def vehicle_spending(request):
    if not request.user.has_module_perm("reports", "read"):
        return HttpResponseForbidden()

    date_from, date_to = parse_dates(request)
    vdept = dept_q(request.user)
    fdept = dept_q(request.user, "vehicle")

    vehicle_filter = request.GET.get("vehicle", "")
    vehicles = Vehicle.objects.filter(**vdept).order_by("plate_number")
    filtered_vehicles = vehicles.filter(pk=vehicle_filter) if vehicle_filter else vehicles

    rows = []
    for v in filtered_vehicles:
        fuel  = FuelLog.objects.filter(vehicle=v, fuel_date__range=[date_from, date_to]).aggregate(
            litres=Sum("actual_litres"), cost=Sum("actual_cost"), count=Count("id"))
        maint = MaintenanceRecord.objects.filter(vehicle=v, service_date__range=[date_from, date_to]).aggregate(
            cost=Sum("total_cost"), count=Count("id"))
        fuel_cost  = fuel["cost"]  or Decimal("0")
        maint_cost = maint["cost"] or Decimal("0")
        total      = fuel_cost + maint_cost
        if total > 0 or request.GET.get("show_all"):
            rows.append({
                "vehicle":     v,
                "fuel_litres": fuel["litres"] or 0,
                "fuel_cost":   fuel_cost,
                "fuel_count":  fuel["count"],
                "maint_cost":  maint_cost,
                "maint_count": maint["count"],
                "total":       total,
            })
    rows.sort(key=lambda x: x["total"], reverse=True)
    grand_fuel  = sum(r["fuel_cost"]  for r in rows)
    grand_maint = sum(r["maint_cost"] for r in rows)
    grand_total = grand_fuel + grand_maint

    fmt = request.GET.get("format", "")
    if fmt == "excel":
        return _vehicle_spending_excel(rows, date_from, date_to, grand_fuel, grand_maint, grand_total)
    if fmt == "pdf":
        return _vehicle_spending_pdf(request, rows, date_from, date_to, grand_fuel, grand_maint, grand_total)

    return render(request, "reports/vehicle_spending.html", {
        "rows": rows, "date_from": date_from, "date_to": date_to,
        "grand_fuel": grand_fuel, "grand_maint": grand_maint, "grand_total": grand_total,
        "vehicles": vehicles, "vehicle_filter": vehicle_filter,
    })


def _vehicle_spending_excel(rows, df, dt, gf, gm, gt):
    n_cols = 8
    wb, ws = xl_workbook("Vehicle Spending")
    xl_title_block(ws, "Per-Vehicle Spending Report", "All Vehicles", df, dt, n_cols=n_cols)
    cols = ["Plate No.", "Make & Model", "Department", "Fuel Litres", "Fuel Cost (₦)", "Maint. Cost (₦)", "Total Spend (₦)", "Maint. Records"]
    xl_header_row(ws, cols, row=7)
    for i, r in enumerate(rows, 8):
        xl_data_row(ws, [
            r["vehicle"].plate_number,
            f"{r['vehicle'].make} {r['vehicle'].model}",
            r["vehicle"].department.name,
            float(r["fuel_litres"]),
            float(r["fuel_cost"]),
            float(r["maint_cost"]),
            float(r["total"]),
            r["maint_count"],
        ], i, shade=(i % 2 == 0))
    totals_row = len(rows) + 8
    xl_totals_row(ws, totals_row, n_cols, label_col=1,
                  value_cols=[5, 6, 7],
                  values=[float(gf), float(gm), float(gt)])
    col_widths = [15, 24, 22, 14, 18, 18, 18, 14]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    return xl_response(wb, f"vehicle_spending_{df}_{dt}.xlsx")


def _vehicle_spending_pdf(request, rows, df, dt, gf, gm, gt):
    return render(request, "reports/pdf/vehicle_spending.html", {
        "rows": rows, "date_from": df, "date_to": dt,
        "grand_fuel": gf, "grand_maint": gm, "grand_total": gt,
    })


# ═══════════════════════════════════════════════════════════════════════
# REPORT 2 — Fleet Spending Summary
# ═══════════════════════════════════════════════════════════════════════

@login_required
def fleet_summary(request):
    if not request.user.has_module_perm("reports", "read"):
        return HttpResponseForbidden()

    date_from, date_to = parse_dates(request)
    fdept = dept_q(request.user, "vehicle")

    fuel_qs  = FuelLog.objects.filter(fuel_date__range=[date_from, date_to], **fdept)
    maint_qs = MaintenanceRecord.objects.filter(service_date__range=[date_from, date_to], **fdept)

    total_fuel_cost   = fuel_qs.aggregate(t=Sum("actual_cost"))["t"] or 0
    total_fuel_litres = fuel_qs.aggregate(t=Sum("actual_litres"))["t"] or 0
    total_maint_cost  = maint_qs.aggregate(t=Sum("total_cost"))["t"] or 0
    total_spend       = total_fuel_cost + total_maint_cost
    total_coupons     = FuelCoupon.objects.filter(issue_datetime__date__gte=date_from, issue_datetime__date__lte=date_to, **fdept).count()
    total_maint_recs  = maint_qs.count()

    # By department
    dept_rows = []
    for dept in Department.objects.filter(is_active=True):
        fc = FuelLog.objects.filter(fuel_date__range=[date_from, date_to], vehicle__department=dept).aggregate(t=Sum("actual_cost"))["t"] or 0
        mc = MaintenanceRecord.objects.filter(service_date__range=[date_from, date_to], vehicle__department=dept).aggregate(t=Sum("total_cost"))["t"] or 0
        if fc > 0 or mc > 0:
            dept_rows.append({"dept": dept, "fuel": fc, "maint": mc, "total": fc + mc})
    dept_rows.sort(key=lambda x: x["total"], reverse=True)

    # By service type
    maint_by_type = []
    for val, label in MaintenanceRecord.SERVICE_CHOICES:
        cost = maint_qs.filter(service_type=val).aggregate(t=Sum("total_cost"))["t"] or 0
        if cost > 0:
            maint_by_type.append({"label": label, "cost": cost})
    maint_by_type.sort(key=lambda x: x["cost"], reverse=True)

    ctx = {
        "date_from": date_from, "date_to": date_to,
        "total_fuel_cost": total_fuel_cost, "total_fuel_litres": total_fuel_litres,
        "total_maint_cost": total_maint_cost, "total_spend": total_spend,
        "total_coupons": total_coupons, "total_maint_recs": total_maint_recs,
        "dept_rows": dept_rows, "maint_by_type": maint_by_type,
    }

    fmt = request.GET.get("format", "")
    if fmt == "excel":
        return _fleet_summary_excel(ctx)
    if fmt == "pdf":
        return _fleet_summary_pdf(request, ctx)

    return render(request, "reports/fleet_summary.html", ctx)


def _fleet_summary_excel(ctx):
    df, dt = ctx["date_from"], ctx["date_to"]
    n_cols = 4
    wb, ws = xl_workbook("Fleet Summary")
    xl_title_block(ws, "Fleet Spending Summary", "University-wide overview", df, dt, n_cols=n_cols)
    ws.sheet_view.showGridLines = False

    # KPI block starts at row 8 (after 6-row title block + spacer)
    kpi_header_fill = PatternFill("solid", fgColor=NAVY2)
    ws.cell(8, 1, "SUMMARY METRICS").font = Font(bold=True, size=10, color=WHITE, name="Calibri")
    ws.cell(8, 1).fill = kpi_header_fill
    ws.cell(8, 2, "VALUE").font = Font(bold=True, size=10, color=WHITE, name="Calibri")
    ws.cell(8, 2).fill = kpi_header_fill
    ws.row_dimensions[8].height = 22
    kpis = [
        ("Total Fuel Cost (₦)",       float(ctx["total_fuel_cost"])),
        ("Total Fuel Litres",          float(ctx["total_fuel_litres"] or 0)),
        ("Total Maintenance Cost (₦)", float(ctx["total_maint_cost"])),
        ("Grand Total Spend (₦)",      float(ctx["total_spend"])),
        ("Coupons Issued",             ctx["total_coupons"]),
        ("Maintenance Records",        ctx["total_maint_recs"]),
    ]
    for i, (k, v) in enumerate(kpis, 9):
        shade = (i % 2 == 0)
        fill = PatternFill("solid", fgColor=STRIPE if shade else WHITE)
        c1 = ws.cell(i, 1, k)
        c1.font = Font(size=10, name="Calibri")
        c1.fill = fill
        c1.alignment = Alignment(indent=1, vertical="center")
        c2 = ws.cell(i, 2, v)
        c2.font = Font(size=10, name="Calibri")
        c2.fill = fill
        c2.alignment = Alignment(horizontal="right", vertical="center")
        if isinstance(v, float):
            c2.number_format = '#,##0.00'
        ws.row_dimensions[i].height = 18

    # Department breakdown — starts after KPI block (row 8 header + 6 KPI rows = row 16)
    row = 16
    ws.cell(row, 1, "BREAKDOWN BY DEPARTMENT").font = Font(bold=True, size=10, color=WHITE, name="Calibri")
    ws.cell(row, 1).fill = PatternFill("solid", fgColor=BROWN)
    ws.row_dimensions[row].height = 20
    row += 1
    xl_header_row(ws, ["Department", "Fuel Cost (₦)", "Maint. Cost (₦)", "Total (₦)"], row)
    row += 1
    for i, r in enumerate(ctx["dept_rows"], row):
        xl_data_row(ws, [r["dept"].name, float(r["fuel"]), float(r["maint"]), float(r["total"])], i, shade=(i%2==0))
        row += 1
    xl_totals_row(ws, row, n_cols, label_col=1,
                  value_cols=[2, 3, 4],
                  values=[float(ctx["total_fuel_cost"]), float(ctx["total_maint_cost"]), float(ctx["total_spend"])])

    for col, w in zip(["A","B","C","D"], [30, 20, 20, 20]):
        ws.column_dimensions[col].width = w
    return xl_response(wb, f"fleet_summary_{df}_{dt}.xlsx")


def _fleet_summary_pdf(request, ctx):
    return render(request, "reports/pdf/fleet_summary.html", ctx)


# ═══════════════════════════════════════════════════════════════════════
# REPORT 3 — Monthly Expense Report
# ═══════════════════════════════════════════════════════════════════════

@login_required
def monthly_expense(request):
    if not request.user.has_module_perm("reports", "read"):
        return HttpResponseForbidden()

    date_from, date_to = parse_dates(request)
    fdept = dept_q(request.user, "vehicle")

    fuel_logs = FuelLog.objects.filter(
        fuel_date__range=[date_from, date_to], **fdept
    ).select_related("vehicle", "driver", "coupon").order_by("fuel_date")

    maint_records = MaintenanceRecord.objects.filter(
        service_date__range=[date_from, date_to], **fdept
    ).select_related("vehicle", "vendor").order_by("service_date")

    total_fuel  = sum(l.actual_cost for l in fuel_logs)
    total_maint = sum(r.total_cost  for r in maint_records)
    total_spend = total_fuel + total_maint

    ctx = {
        "date_from": date_from, "date_to": date_to,
        "fuel_logs": fuel_logs, "maint_records": maint_records,
        "total_fuel": total_fuel, "total_maint": total_maint, "total_spend": total_spend,
    }

    fmt = request.GET.get("format", "")
    if fmt == "excel":
        return _monthly_expense_excel(ctx)
    if fmt == "pdf":
        return render(request, "reports/pdf/monthly_expense.html", ctx)

    return render(request, "reports/monthly_expense.html", ctx)


def _monthly_expense_excel(ctx):
    df, dt = ctx["date_from"], ctx["date_to"]
    n_cols = 6
    wb = openpyxl.Workbook()

    # Sheet 1 — Fuel logs
    ws1 = wb.active
    ws1.title = "Fuel Transactions"
    ws1.sheet_view.showGridLines = False
    xl_title_block(ws1, "Monthly Fuel Transactions", "Fuel log detail", df, dt, n_cols=n_cols)
    xl_header_row(ws1, ["Date", "Coupon ID", "Vehicle", "Driver", "Litres", "Cost (₦)"], 7)
    for i, log in enumerate(ctx["fuel_logs"], 8):
        xl_data_row(ws1, [
            str(log.fuel_date), log.coupon.coupon_id,
            log.vehicle.plate_number, log.driver.full_name,
            float(log.actual_litres), float(log.actual_cost),
        ], i, shade=(i%2==0))
    totals_row1 = len(ctx["fuel_logs"]) + 8
    xl_totals_row(ws1, totals_row1, n_cols, label_col=1,
                  value_cols=[5, 6],
                  values=[float(sum(l.actual_litres for l in ctx["fuel_logs"])),
                          float(ctx["total_fuel"])])
    for col, w in zip(["A","B","C","D","E","F"], [14, 24, 14, 22, 12, 16]):
        ws1.column_dimensions[col].width = w

    # Sheet 2 — Maintenance
    ws2 = wb.create_sheet("Maintenance")
    ws2.sheet_view.showGridLines = False
    xl_title_block(ws2, "Monthly Maintenance Records", "Maintenance detail", df, dt, n_cols=n_cols)
    xl_header_row(ws2, ["Date", "Vehicle", "Service Type", "Vendor", "Cost (₦)", "Approved By"], 7)
    for i, rec in enumerate(ctx["maint_records"], 8):
        xl_data_row(ws2, [
            str(rec.service_date), rec.vehicle.plate_number,
            rec.get_service_type_display(), rec.effective_vendor_name,
            float(rec.total_cost), rec.approved_by,
        ], i, shade=(i%2==0))
    totals_row2 = len(ctx["maint_records"]) + 8
    xl_totals_row(ws2, totals_row2, n_cols, label_col=1,
                  value_cols=[5],
                  values=[float(ctx["total_maint"])])
    for col, w in zip(["A","B","C","D","E","F"], [14, 16, 20, 22, 16, 20]):
        ws2.column_dimensions[col].width = w

    return xl_response(wb, f"monthly_expense_{df}_{dt}.xlsx")


# ═══════════════════════════════════════════════════════════════════════
# REPORT 4 — Fuel Coupon Report
# ═══════════════════════════════════════════════════════════════════════

@login_required
def coupon_report(request):
    if not request.user.has_module_perm("reports", "read"):
        return HttpResponseForbidden()

    date_from, date_to = parse_dates(request)
    fdept = dept_q(request.user, "vehicle")

    coupons = FuelCoupon.objects.filter(
        issue_datetime__date__gte=date_from,
        issue_datetime__date__lte=date_to,
        **fdept
    ).select_related("vehicle", "driver", "fuel_station", "issued_by").order_by("-issue_datetime")

    by_status = {s: coupons.filter(status=s).count() for s, _ in FuelCoupon.STATUS_CHOICES}
    total_value   = coupons.aggregate(t=Sum("total_value"))["t"] or 0
    redeemed_cost = FuelLog.objects.filter(
        coupon__in=coupons.filter(status=FuelCoupon.STATUS_REDEEMED)
    ).aggregate(t=Sum("actual_cost"))["t"] or 0

    ctx = {
        "date_from": date_from, "date_to": date_to,
        "coupons": coupons, "by_status": by_status,
        "total_value": total_value, "redeemed_cost": redeemed_cost,
    }

    fmt = request.GET.get("format", "")
    if fmt == "excel":
        return _coupon_report_excel(ctx)
    if fmt == "pdf":
        return render(request, "reports/pdf/coupon_report.html", ctx)

    return render(request, "reports/coupon_report.html", ctx)


def _coupon_report_excel(ctx):
    df, dt = ctx["date_from"], ctx["date_to"]
    n_cols = 8
    wb, ws = xl_workbook("Coupon Report")
    ws.sheet_view.showGridLines = False
    xl_title_block(ws, "Fuel Coupon Report", "All issued coupons", df, dt, n_cols=n_cols)
    xl_header_row(ws, ["Coupon ID", "Issued", "Vehicle", "Driver", "Station", "Litres", "Value (₦)", "Status"], 7)
    for i, c in enumerate(ctx["coupons"], 8):
        xl_data_row(ws, [
            c.coupon_id, c.issue_datetime.strftime("%d/%m/%Y %H:%M"),
            c.vehicle.plate_number, c.driver.full_name, c.fuel_station.name,
            float(c.litres), float(c.total_value), c.get_status_display(),
        ], i, shade=(i%2==0))
    totals_row = len(ctx["coupons"]) + 8
    xl_totals_row(ws, totals_row, n_cols, label_col=1,
                  value_cols=[7],
                  values=[float(ctx["total_value"])])
    for col, w in zip(["A","B","C","D","E","F","G","H"], [24, 18, 14, 22, 22, 10, 16, 12]):
        ws.column_dimensions[col].width = w
    return xl_response(wb, f"coupon_report_{df}_{dt}.xlsx")


# ═══════════════════════════════════════════════════════════════════════
# REPORT 5 — Maintenance History
# ═══════════════════════════════════════════════════════════════════════

@login_required
def maintenance_report(request):
    if not request.user.has_module_perm("reports", "read"):
        return HttpResponseForbidden()

    date_from, date_to = parse_dates(request)
    fdept = dept_q(request.user, "vehicle")

    records = MaintenanceRecord.objects.filter(
        service_date__range=[date_from, date_to], **fdept
    ).select_related("vehicle", "vendor", "created_by").order_by("-service_date")

    total_cost = records.aggregate(t=Sum("total_cost"))["t"] or 0
    by_type    = {}
    for val, label in MaintenanceRecord.SERVICE_CHOICES:
        cost = records.filter(service_type=val).aggregate(t=Sum("total_cost"))["t"] or 0
        if cost > 0:
            by_type[label] = cost

    ctx = {
        "date_from": date_from, "date_to": date_to,
        "records": records, "total_cost": total_cost, "by_type": by_type,
    }

    fmt = request.GET.get("format", "")
    if fmt == "excel":
        return _maintenance_excel(ctx)
    if fmt == "pdf":
        return render(request, "reports/pdf/maintenance_report.html", ctx)

    return render(request, "reports/maintenance_report.html", ctx)


def _maintenance_excel(ctx):
    df, dt = ctx["date_from"], ctx["date_to"]
    n_cols = 8
    wb, ws = xl_workbook("Maintenance History")
    ws.sheet_view.showGridLines = False
    xl_title_block(ws, "Maintenance History Report", "All maintenance records", df, dt, n_cols=n_cols)
    xl_header_row(ws, ["Date", "Vehicle", "Plate", "Service Type", "Description", "Vendor", "Cost (₦)", "Approved By"], 7)
    for i, r in enumerate(ctx["records"], 8):
        xl_data_row(ws, [
            str(r.service_date),
            f"{r.vehicle.make} {r.vehicle.model}", r.vehicle.plate_number,
            r.get_service_type_display(), r.description[:60],
            r.effective_vendor_name, float(r.total_cost), r.approved_by,
        ], i, shade=(i%2==0))
    totals_row = len(ctx["records"]) + 8
    xl_totals_row(ws, totals_row, n_cols, label_col=1,
                  value_cols=[7],
                  values=[float(ctx["total_cost"])])
    for col, w in zip(["A","B","C","D","E","F","G","H"], [13, 22, 14, 18, 32, 22, 16, 20]):
        ws.column_dimensions[col].width = w
    return xl_response(wb, f"maintenance_report_{df}_{dt}.xlsx")


# ═══════════════════════════════════════════════════════════════════════
# REPORT 6 — Vendor Spend Report
# ═══════════════════════════════════════════════════════════════════════

@login_required
def vendor_report(request):
    if not request.user.has_module_perm("reports", "read"):
        return HttpResponseForbidden()

    date_from, date_to = parse_dates(request)
    fdept = dept_q(request.user, "vehicle")

    rows = []
    for vendor in Vendor.objects.all().order_by("name"):
        fuel  = FuelLog.objects.filter(fuel_station=vendor, fuel_date__range=[date_from, date_to], **fdept).aggregate(
            cost=Sum("actual_cost"), litres=Sum("actual_litres"), count=Count("id"))
        maint = MaintenanceRecord.objects.filter(vendor=vendor, service_date__range=[date_from, date_to], **fdept).aggregate(
            cost=Sum("total_cost"), count=Count("id"))
        fc = fuel["cost"]  or Decimal("0")
        mc = maint["cost"] or Decimal("0")
        if fc > 0 or mc > 0:
            rows.append({
                "vendor": vendor, "fuel_cost": fc, "fuel_litres": fuel["litres"] or 0,
                "fuel_txn": fuel["count"], "maint_cost": mc, "maint_txn": maint["count"],
                "total": fc + mc,
            })
    rows.sort(key=lambda x: x["total"], reverse=True)
    grand_total = sum(r["total"] for r in rows)

    ctx = {
        "date_from": date_from, "date_to": date_to,
        "rows": rows, "grand_total": grand_total,
    }

    fmt = request.GET.get("format", "")
    if fmt == "excel":
        return _vendor_excel(ctx)
    if fmt == "pdf":
        return render(request, "reports/pdf/vendor_report.html", ctx)

    return render(request, "reports/vendor_report.html", ctx)


def _vendor_excel(ctx):
    df, dt = ctx["date_from"], ctx["date_to"]
    n_cols = 8
    wb, ws = xl_workbook("Vendor Spend")
    ws.sheet_view.showGridLines = False
    xl_title_block(ws, "Vendor Spend Report", "All active vendors", df, dt, n_cols=n_cols)
    xl_header_row(ws, ["Vendor", "Type", "Fuel Cost (₦)", "Litres", "Fuel Txns", "Maint. Cost (₦)", "Maint. Txns", "Total (₦)"], 7)
    for i, r in enumerate(ctx["rows"], 8):
        xl_data_row(ws, [
            r["vendor"].name, r["vendor"].get_type_display(),
            float(r["fuel_cost"]), float(r["fuel_litres"]),
            r["fuel_txn"], float(r["maint_cost"]), r["maint_txn"], float(r["total"]),
        ], i, shade=(i%2==0))
    totals_row = len(ctx["rows"]) + 8
    xl_totals_row(ws, totals_row, n_cols, label_col=1,
                  value_cols=[8],
                  values=[float(ctx["grand_total"])])
    for col, w in zip(["A","B","C","D","E","F","G","H"], [28, 16, 18, 12, 12, 18, 12, 18]):
        ws.column_dimensions[col].width = w
    return xl_response(wb, f"vendor_report_{df}_{dt}.xlsx")
