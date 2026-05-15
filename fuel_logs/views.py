from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import FuelLog
from coupons.models import FuelCoupon
from audit.models import AuditLog


def dept_filter(user):
    """
    Vehicle logs scope by vehicle.department. Generator logs are
    organisation-wide, so they're always included. Returns a Q object.
    """
    from django.db.models import Q
    if user.is_system_admin or not user.department:
        return Q()
    return Q(generator__isnull=False) | Q(vehicle__department=user.department)


@login_required
def list_view(request):
    if not request.user.has_module_perm("fuel_logs", "read"):
        return HttpResponseForbidden()

    qs = FuelLog.objects.select_related(
        "vehicle", "driver", "generator", "coupon", "fuel_station", "logged_by"
    ).filter(dept_filter(request.user))

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(coupon__coupon_id__icontains=q) |
            Q(vehicle__plate_number__icontains=q) |
            Q(driver__full_name__icontains=q) |
            Q(generator__tag__icontains=q) |
            Q(generator__name__icontains=q)
        )

    return render(request, "fuel_logs/list.html", {
        "logs": qs[:100],
        "q": q,
        "can_write": request.user.has_module_perm("fuel_logs", "write"),
    })


@login_required
def create_view(request):
    if not request.user.has_module_perm("fuel_logs", "write"):
        return HttpResponseForbidden()

    # Coupon statuses eligible for redemption: Approved (new workflow) or Issued (legacy).
    REDEEMABLE_STATUSES = (FuelCoupon.STATUS_APPROVED, FuelCoupon.STATUS_ISSUED)

    # Pre-fill coupon if passed as query param
    preselect_coupon_str = request.GET.get("coupon", "")
    prefilled = None
    if preselect_coupon_str:
        prefilled = FuelCoupon.objects.filter(
            Q(coupon_id=preselect_coupon_str) | Q(verification_code=preselect_coupon_str.upper()),
            status__in=REDEEMABLE_STATUSES,
        ).first()

    if request.method == "POST":
        errors = {}
        coupon_id_input = request.POST.get("coupon_id", "").strip()
        fuel_date       = request.POST.get("fuel_date", "").strip()
        notes           = request.POST.get("notes", "").strip()

        coupon = None
        if not coupon_id_input:
            errors["coupon_id"] = "Coupon ID or verification code is required."
        else:
            coupon = FuelCoupon.objects.filter(
                Q(coupon_id__iexact=coupon_id_input) |
                Q(verification_code__iexact=coupon_id_input.upper())
            ).first()
            if not coupon:
                errors["coupon_id"] = "No coupon found with that ID or code."
            elif coupon.status not in REDEEMABLE_STATUSES:
                errors["coupon_id"] = f"This coupon is {coupon.get_status_display()} and cannot be redeemed."
            elif coupon.is_expired_by_date:
                errors["coupon_id"] = "This coupon has expired. Cancel it and issue a new one."

        if not fuel_date: errors["fuel_date"] = "Fuel date is required."

        if not errors and coupon:
            # Actual litres / cost are taken straight from the approved coupon —
            # since the approver has already set the authorised amount, there's
            # no separate "actual" reading captured at the pump.
            log = FuelLog.objects.create(
                coupon        = coupon,
                actual_litres = coupon.litres,
                actual_cost   = coupon.total_value,
                fuel_date     = fuel_date,
                notes         = notes,
                logged_by     = request.user,
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_REDEEM, module="fuel_logs",
                record_id=str(log.pk),
                detail=f"Redeemed coupon {coupon.coupon_id} for {coupon.asset_label}"
            )
            messages.success(request, f"Coupon {coupon.coupon_id} redeemed. Fuel log saved.")
            return redirect("fuel_logs:list")

        return render(request, "fuel_logs/form.html", {
            "errors": errors,
            "coupon_id_val":    coupon_id_input,
            "fuel_date_val":    fuel_date,
            "notes_val":        notes,
            "prefilled":        coupon if coupon and coupon.status in REDEEMABLE_STATUSES else None,
        })

    return render(request, "fuel_logs/form.html", {
        "prefilled":     prefilled,
        "coupon_id_val": prefilled.coupon_id if prefilled else "",
        "fuel_date_val": "",
        "notes_val":     "",
    })
