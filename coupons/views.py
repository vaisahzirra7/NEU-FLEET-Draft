from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import FuelCoupon
from vehicles.models import Vehicle
from generators.models import Generator
from drivers.models import Driver
from vendors.models import Vendor
from audit.models import AuditLog


def dept_filter(user):
    """
    Department scoping for coupons.

    Vehicle coupons are filtered to the user's department via the vehicle FK.
    Generator coupons are NOT department-scoped (generators are organisation-wide
    per the institutional design — see Gen-1), so all generator coupons are
    visible to anyone with the 'coupons' read permission.

    Returns a Q object suitable for `qs.filter(...)`. Callers should use:
        qs.filter(dept_filter(request.user))   # NOT **dept_filter(...)
    """
    from django.db.models import Q
    if user.is_system_admin or not user.department:
        return Q()
    return Q(generator__isnull=False) | Q(vehicle__department=user.department)


@login_required
def list_view(request):
    if not request.user.has_module_perm("coupons", "read"):
        return HttpResponseForbidden()

    qs = FuelCoupon.objects.select_related(
        "vehicle", "driver", "generator", "fuel_station", "issued_by"
    ).filter(dept_filter(request.user))

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(coupon_id__icontains=q) |
            Q(verification_code__icontains=q) |
            Q(vehicle__plate_number__icontains=q) |
            Q(driver__full_name__icontains=q) |
            Q(generator__tag__icontains=q) |
            Q(generator__name__icontains=q)
        )

    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)

    return render(request, "coupons/list.html", {
        "coupons": qs[:100],
        "q": q,
        "status_filter": status,
        "status_choices": FuelCoupon.STATUS_CHOICES,
        "can_write": request.user.has_module_perm("coupons", "write"),
    })


@login_required
def create_view(request):
    if not request.user.has_module_perm("coupons", "write"):
        return HttpResponseForbidden()

    dept_q = {} if request.user.is_system_admin or not request.user.department else {"department": request.user.department}
    vehicles      = Vehicle.objects.filter(status=Vehicle.STATUS_ACTIVE, **dept_q).select_related("default_driver").order_by("plate_number")
    drivers       = Driver.objects.filter(status=Driver.STATUS_ACTIVE).order_by("full_name")
    generators    = Generator.objects.filter(status=Generator.STATUS_ACTIVE).order_by("tag")
    fuel_stations = Vendor.objects.filter(type=Vendor.TYPE_FUEL, is_active=True).order_by("name")

    preselect_vehicle   = request.GET.get("vehicle", "")
    preselect_generator = request.GET.get("generator", "")
    # Default tab: generator if preselected, else vehicle
    default_asset_type  = "generator" if preselect_generator else "vehicle"

    if request.method == "POST":
        errors = {}
        asset_type     = request.POST.get("asset_type", "vehicle").strip()
        vehicle_id     = request.POST.get("vehicle", "")
        driver_id      = request.POST.get("driver", "")
        generator_id   = request.POST.get("generator", "")
        station_id     = request.POST.get("fuel_station", "")
        litres_raw     = request.POST.get("litres", "").strip()
        cost_raw       = request.POST.get("cost_per_litre", "").strip()
        expiry_date    = request.POST.get("expiry_date", "").strip()
        purpose        = request.POST.get("purpose", "").strip()

        # ── Validate asset based on type ──
        if asset_type == "generator":
            if not generator_id: errors["generator"] = "Generator is required."
            # Force driver/vehicle to None for generator coupons regardless of stray form data
            vehicle_id = ""
            driver_id  = ""
        else:
            asset_type = "vehicle"  # normalise
            if not vehicle_id: errors["vehicle"] = "Vehicle is required."
            if not driver_id:  errors["driver"]  = "Driver is required."
            generator_id = ""

        if not station_id:  errors["fuel_station"]   = "Fuel station is required."
        if not litres_raw:  errors["litres"]         = "Litres is required."
        if not cost_raw:    errors["cost_per_litre"] = "Cost per litre is required."

        litres = cost = None
        if litres_raw:
            try:
                litres = Decimal(litres_raw)
                if litres <= 0:
                    errors["litres"] = "Litres must be greater than zero."
            except InvalidOperation:
                errors["litres"] = "Enter a valid number."

        if cost_raw:
            try:
                cost = Decimal(cost_raw)
                if cost <= 0:
                    errors["cost_per_litre"] = "Cost must be greater than zero."
            except InvalidOperation:
                errors["cost_per_litre"] = "Enter a valid number."

        if not errors:
            total = litres * cost
            coupon = FuelCoupon.objects.create(
                vehicle_id      = vehicle_id or None,
                driver_id       = driver_id or None,
                generator_id    = generator_id or None,
                fuel_station_id = station_id,
                issued_by       = request.user,
                litres          = litres,
                cost_per_litre  = cost,
                total_value     = total,
                expiry_date     = expiry_date or None,
                purpose         = purpose,
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_ISSUE, module="coupons",
                record_id=str(coupon.pk),
                detail=f"Issued coupon {coupon.coupon_id} for {coupon.asset_label}"
            )

            # Auto-dismiss monthly fuel reminder only applies to vehicles
            if coupon.is_for_vehicle and coupon.vehicle.needs_monthly_fuel:
                from vehicles.models import MonthlyFuelDismissal
                from django.utils import timezone as tz
                now = tz.now()
                MonthlyFuelDismissal.objects.get_or_create(
                    vehicle=coupon.vehicle, month=now.month, year=now.year,
                    defaults={"dismissed_by": request.user.full_name}
                )

            messages.success(request, f"Coupon {coupon.coupon_id} submitted for approval.")
            return redirect("coupons:detail", pk=coupon.pk)

        return render(request, "coupons/form.html", {
            "errors": errors,
            "vehicles": vehicles,
            "drivers": drivers,
            "generators": generators,
            "fuel_stations": fuel_stations,
            "post": request.POST,
            "default_asset_type": asset_type,
        })

    return render(request, "coupons/form.html", {
        "vehicles": vehicles,
        "drivers": drivers,
        "generators": generators,
        "fuel_stations": fuel_stations,
        "preselect_vehicle":   preselect_vehicle,
        "preselect_generator": preselect_generator,
        "default_asset_type":  default_asset_type,
        "post": {},
    })


@login_required
def bulk_issue_view(request):
    """Bulk coupon issuance — issue coupons to multiple vehicles OR generators at once."""
    if not request.user.has_module_perm("coupons", "write"):
        return HttpResponseForbidden()

    dept_q        = {} if request.user.is_system_admin or not request.user.department else {"department": request.user.department}
    vehicles      = Vehicle.objects.filter(status=Vehicle.STATUS_ACTIVE, **dept_q).select_related("default_driver", "department").order_by("plate_number")
    generators    = Generator.objects.filter(status=Generator.STATUS_ACTIVE).order_by("tag")
    fuel_stations = Vendor.objects.filter(type=Vendor.TYPE_FUEL, is_active=True).order_by("name")
    drivers       = Driver.objects.filter(status=Driver.STATUS_ACTIVE).order_by("full_name")

    if request.method == "POST":
        asset_type      = request.POST.get("asset_type", "vehicle").strip()
        station_id      = request.POST.get("fuel_station", "")
        cost_raw        = request.POST.get("cost_per_litre", "").strip()
        expiry_date     = request.POST.get("expiry_date", "").strip()

        errors = {}
        if not station_id:  errors["fuel_station"]   = "Fuel station is required."
        if not cost_raw:    errors["cost_per_litre"] = "Cost per litre is required."

        cost = None
        if cost_raw:
            try:
                cost = Decimal(cost_raw)
                if cost <= 0:
                    errors["cost_per_litre"] = "Cost must be greater than zero."
            except InvalidOperation:
                errors["cost_per_litre"] = "Enter a valid number."

        # Per-asset litres validation, depending on tab
        rows = []  # list of (asset_kind, asset_id, driver_id_or_None, litres)
        if asset_type == "generator":
            generator_ids = request.POST.getlist("generator_ids")
            if not generator_ids:
                errors["assets"] = "Select at least one generator."
            else:
                for gid in generator_ids:
                    litres_raw = request.POST.get(f"litres_gen_{gid}", "").strip()
                    if not litres_raw:
                        errors[f"litres_gen_{gid}"] = f"Litres required for generator {gid}."
                        continue
                    try:
                        litres = Decimal(litres_raw)
                        if litres <= 0:
                            errors[f"litres_gen_{gid}"] = "Must be > 0."
                            continue
                    except InvalidOperation:
                        errors[f"litres_gen_{gid}"] = "Invalid number."
                        continue
                    rows.append(("generator", gid, None, litres))
        else:
            asset_type = "vehicle"
            vehicle_ids = request.POST.getlist("vehicle_ids")
            if not vehicle_ids:
                errors["assets"] = "Select at least one vehicle."
            else:
                for vid in vehicle_ids:
                    litres_raw = request.POST.get(f"litres_{vid}", "").strip()
                    driver_id  = request.POST.get(f"driver_{vid}", "")
                    if not litres_raw:
                        errors[f"litres_{vid}"] = f"Litres required for vehicle {vid}."
                        continue
                    try:
                        litres = Decimal(litres_raw)
                        if litres <= 0:
                            errors[f"litres_{vid}"] = "Must be > 0."
                            continue
                    except InvalidOperation:
                        errors[f"litres_{vid}"] = "Invalid number."
                        continue
                    rows.append(("vehicle", vid, driver_id or None, litres))

        if not errors:
            issued = []
            for kind, asset_id, driver_id, litres in rows:
                total = litres * cost
                if kind == "vehicle":
                    coupon = FuelCoupon.objects.create(
                        vehicle_id      = asset_id,
                        driver_id       = driver_id,
                        fuel_station_id = station_id,
                        litres          = litres,
                        cost_per_litre  = cost,
                        total_value     = total,
                        expiry_date     = expiry_date or None,
                        purpose         = "Bulk issue",
                        issued_by       = request.user,
                    )
                    try:
                        v = Vehicle.objects.get(pk=asset_id)
                        if v.needs_monthly_fuel:
                            from vehicles.models import MonthlyFuelDismissal
                            from django.utils import timezone as tz
                            now = tz.now()
                            MonthlyFuelDismissal.objects.get_or_create(
                                vehicle=v, month=now.month, year=now.year,
                                defaults={"dismissed_by": request.user.full_name}
                            )
                    except Vehicle.DoesNotExist:
                        pass
                    detail = f"Bulk issued coupon {coupon.coupon_id} for vehicle #{asset_id}"
                else:
                    coupon = FuelCoupon.objects.create(
                        generator_id    = asset_id,
                        fuel_station_id = station_id,
                        litres          = litres,
                        cost_per_litre  = cost,
                        total_value     = total,
                        expiry_date     = expiry_date or None,
                        purpose         = "Bulk issue",
                        issued_by       = request.user,
                    )
                    detail = f"Bulk issued coupon {coupon.coupon_id} for generator #{asset_id}"

                AuditLog.objects.create(
                    user=request.user, user_name=request.user.full_name,
                    action=AuditLog.ACTION_ISSUE, module="coupons",
                    record_id=str(coupon.pk),
                    detail=detail,
                )
                issued.append(coupon)

            messages.success(
                request,
                f"{len(issued)} coupon{'s' if len(issued) != 1 else ''} submitted for approval."
            )
            if request.user.has_module_perm("coupons", "approve"):
                return redirect("coupons:pending_list")
            return redirect("coupons:list")

        return render(request, "coupons/bulk_issue.html", {
            "vehicles": vehicles,
            "generators": generators,
            "fuel_stations": fuel_stations,
            "drivers": drivers,
            "errors": errors,
            "post": request.POST,
            "default_asset_type": asset_type,
        })

    return render(request, "coupons/bulk_issue.html", {
        "vehicles": vehicles,
        "generators": generators,
        "fuel_stations": fuel_stations,
        "drivers": drivers,
        "errors": {},
        "post": {},
        "default_asset_type": "vehicle",
    })


@login_required
def detail_view(request, pk):
    if not request.user.has_module_perm("coupons", "read"):
        return HttpResponseForbidden()

    coupon = get_object_or_404(FuelCoupon, dept_filter(request.user), pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "cancel":
            if not request.user.has_module_perm("coupons", "edit"):
                return HttpResponseForbidden()
            reason = request.POST.get("cancel_reason", "").strip()
            if not reason:
                messages.error(request, "A cancellation reason is required.")
            elif coupon.status not in (FuelCoupon.STATUS_ISSUED, FuelCoupon.STATUS_APPROVED):
                messages.error(request, "Only approved or issued coupons can be cancelled.")
            else:
                coupon.cancel(reason)
                AuditLog.objects.create(
                    user=request.user, user_name=request.user.full_name,
                    action=AuditLog.ACTION_CANCEL, module="coupons",
                    record_id=str(coupon.pk),
                    detail=f"Cancelled coupon {coupon.coupon_id}. Reason: {reason}"
                )
                messages.success(request, f"Coupon {coupon.coupon_id} cancelled.")
                return redirect("coupons:detail", pk=coupon.pk)

    return render(request, "coupons/detail.html", {
        "coupon": coupon,
        "can_edit":    request.user.has_module_perm("coupons", "edit"),
        "can_redeem":  request.user.has_module_perm("fuel_logs", "write"),
        "can_approve": request.user.has_module_perm("coupons", "approve"),
    })


@login_required
def print_slip(request, pk):
    coupon = get_object_or_404(FuelCoupon, dept_filter(request.user), pk=pk)
    if not coupon.is_printable:
        messages.error(
            request,
            f"Coupon {coupon.coupon_id} cannot be printed — current status is "
            f"'{coupon.get_status_display()}'. Coupons must be approved before printing."
        )
        return redirect("coupons:detail", pk=coupon.pk)
    return render(request, "coupons/print_slip.html", {"coupon": coupon})


@login_required
def lookup_ajax(request):
    q = request.GET.get("q", "").strip().upper()
    if not q:
        return JsonResponse({"error": "Enter a coupon ID or verification code."})

    coupon = FuelCoupon.objects.filter(
        Q(coupon_id=q) | Q(verification_code=q)
    ).first()

    if not coupon:
        return JsonResponse({"error": "No coupon found with that ID or code."})
    if coupon.status not in (FuelCoupon.STATUS_ISSUED, FuelCoupon.STATUS_APPROVED):
        return JsonResponse({"error": f"Coupon is {coupon.get_status_display()} and cannot be redeemed."})
    if coupon.is_expired_by_date:
        return JsonResponse({"error": "This coupon has expired. Please cancel it and issue a new one."})

    return JsonResponse({
        "id":          coupon.pk,
        "coupon_id":   coupon.coupon_id,
        "asset_kind":  coupon.asset_kind,
        "asset_label": coupon.asset_label,
        "asset_context": coupon.asset_context_value,  # driver name OR building
        "plate":       coupon.vehicle.plate_number if coupon.is_for_vehicle else "",
        "driver":      coupon.driver.full_name if (coupon.is_for_vehicle and coupon.driver_id) else "",
        "generator":   coupon.generator.tag if coupon.is_for_generator else "",
        "building":    coupon.generator.building if coupon.is_for_generator else "",
        "station":     coupon.fuel_station.name,
        "station_id":  coupon.fuel_station_id,
        "litres":      str(coupon.litres),
        "total_value": str(coupon.total_value),
        "purpose":     coupon.purpose,
    })


# ============================================================
# APPROVAL WORKFLOW VIEWS
# ============================================================

@login_required
def pending_list_view(request):
    """List of all pending coupons awaiting approval/rejection."""
    if not request.user.has_module_perm("coupons", "approve"):
        return HttpResponseForbidden()

    qs = FuelCoupon.objects.select_related(
        "vehicle", "driver", "generator", "fuel_station", "issued_by"
    ).filter(dept_filter(request.user), status=FuelCoupon.STATUS_PENDING)

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(coupon_id__icontains=q) |
            Q(vehicle__plate_number__icontains=q) |
            Q(driver__full_name__icontains=q) |
            Q(generator__tag__icontains=q) |
            Q(issued_by__full_name__icontains=q)
        )

    return render(request, "coupons/pending_list.html", {
        "coupons": qs,
        "q": q,
    })


@login_required
def approve_view(request, pk):
    """Approve a pending coupon. Optionally edit litres / cost_per_litre."""
    if not request.user.has_module_perm("coupons", "approve"):
        return HttpResponseForbidden()

    coupon = get_object_or_404(FuelCoupon, dept_filter(request.user), pk=pk)

    if not coupon.is_pending:
        messages.error(
            request,
            f"Coupon {coupon.coupon_id} is not pending (current status: {coupon.get_status_display()})."
        )
        return redirect("coupons:detail", pk=coupon.pk)

    if request.method == "POST":
        new_litres_raw = request.POST.get("litres", "").strip()
        new_cost_raw   = request.POST.get("cost_per_litre", "").strip()

        errors = {}
        new_litres = new_cost = None

        if new_litres_raw:
            try:
                new_litres = Decimal(new_litres_raw)
                if new_litres <= 0:
                    errors["litres"] = "Litres must be greater than zero."
            except InvalidOperation:
                errors["litres"] = "Enter a valid number."

        if new_cost_raw:
            try:
                new_cost = Decimal(new_cost_raw)
                if new_cost <= 0:
                    errors["cost_per_litre"] = "Cost must be greater than zero."
            except InvalidOperation:
                errors["cost_per_litre"] = "Enter a valid number."

        if errors:
            return render(request, "coupons/approve_form.html", {
                "coupon": coupon, "errors": errors, "post": request.POST,
            })

        # Approve via model method (handles original_* preservation + self-approval flag)
        coupon.approve(
            approver=request.user,
            new_litres=new_litres,
            new_cost_per_litre=new_cost,
        )

        detail_parts = [f"Approved coupon {coupon.coupon_id}"]
        edits = []
        if coupon.original_litres is not None and coupon.original_litres != coupon.litres:
            edits.append(f"litres {coupon.original_litres} → {coupon.litres}")
        if coupon.original_cost_per_litre is not None and coupon.original_cost_per_litre != coupon.cost_per_litre:
            edits.append(f"₦/L {coupon.original_cost_per_litre} → {coupon.cost_per_litre}")
        if edits:
            detail_parts.append("(edited: " + ", ".join(edits) + ")")
        if coupon.is_self_approved:
            detail_parts.append("[SELF-APPROVED]")

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_APPROVE, module="coupons",
            record_id=str(coupon.pk),
            detail=" ".join(detail_parts),
        )

        # Auto-dismiss monthly fuel reminder once approved (vehicles only)
        if coupon.is_for_vehicle and coupon.vehicle.needs_monthly_fuel:
            from vehicles.models import MonthlyFuelDismissal
            from django.utils import timezone as tz
            now = tz.now()
            MonthlyFuelDismissal.objects.get_or_create(
                vehicle=coupon.vehicle, month=now.month, year=now.year,
                defaults={"dismissed_by": request.user.full_name}
            )

        flag_msg = " (self-approval flagged in audit log)" if coupon.is_self_approved else ""
        messages.success(request, f"Coupon {coupon.coupon_id} approved.{flag_msg}")
        return redirect("coupons:pending_list")

    return render(request, "coupons/approve_form.html", {
        "coupon": coupon, "errors": {}, "post": {},
    })


@login_required
def reject_view(request, pk):
    """Reject a pending coupon, with an optional reason."""
    if not request.user.has_module_perm("coupons", "approve"):
        return HttpResponseForbidden()

    coupon = get_object_or_404(FuelCoupon, dept_filter(request.user), pk=pk)

    if not coupon.is_pending:
        messages.error(
            request,
            f"Coupon {coupon.coupon_id} is not pending (current status: {coupon.get_status_display()})."
        )
        return redirect("coupons:detail", pk=coupon.pk)

    if request.method == "POST":
        reason = request.POST.get("rejection_reason", "").strip()
        coupon.reject(approver=request.user, reason=reason)

        detail = f"Rejected coupon {coupon.coupon_id}"
        if reason:
            detail += f". Reason: {reason}"
        if coupon.is_self_approved:
            detail += " [SELF-REJECTED]"

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_REJECT, module="coupons",
            record_id=str(coupon.pk),
            detail=detail,
        )
        messages.success(request, f"Coupon {coupon.coupon_id} rejected.")
        return redirect("coupons:pending_list")

    return redirect("coupons:detail", pk=coupon.pk)


@login_required
def bulk_approve_view(request):
    """Approve multiple pending coupons in one action (no per-coupon edits)."""
    if not request.user.has_module_perm("coupons", "approve"):
        return HttpResponseForbidden()

    if request.method != "POST":
        return redirect("coupons:pending_list")

    ids = request.POST.getlist("coupon_ids")
    if not ids:
        messages.error(request, "No coupons selected.")
        return redirect("coupons:pending_list")

    coupons = FuelCoupon.objects.filter(
        dept_filter(request.user), pk__in=ids, status=FuelCoupon.STATUS_PENDING
    )

    approved_count = 0
    self_approved_count = 0
    for coupon in coupons:
        coupon.approve(approver=request.user)
        approved_count += 1
        if coupon.is_self_approved:
            self_approved_count += 1

        detail = f"Bulk-approved coupon {coupon.coupon_id}"
        if coupon.is_self_approved:
            detail += " [SELF-APPROVED]"
        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_APPROVE, module="coupons",
            record_id=str(coupon.pk),
            detail=detail,
        )

        if coupon.is_for_vehicle and coupon.vehicle.needs_monthly_fuel:
            from vehicles.models import MonthlyFuelDismissal
            from django.utils import timezone as tz
            now = tz.now()
            MonthlyFuelDismissal.objects.get_or_create(
                vehicle=coupon.vehicle, month=now.month, year=now.year,
                defaults={"dismissed_by": request.user.full_name}
            )

    msg = f"{approved_count} coupon{'s' if approved_count != 1 else ''} approved."
    if self_approved_count:
        msg += f" {self_approved_count} self-approval{'s' if self_approved_count != 1 else ''} flagged in audit log."
    messages.success(request, msg)
    return redirect("coupons:pending_list")
