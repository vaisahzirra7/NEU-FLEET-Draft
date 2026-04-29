from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import FuelCoupon
from vehicles.models import Vehicle
from drivers.models import Driver
from vendors.models import Vendor
from audit.models import AuditLog


def dept_filter(user):
    if user.is_system_admin or not user.department:
        return {}
    return {"vehicle__department": user.department}


@login_required
def list_view(request):
    if not request.user.has_module_perm("coupons", "read"):
        return HttpResponseForbidden()

    qs = FuelCoupon.objects.select_related(
        "vehicle", "driver", "fuel_station", "issued_by"
    ).filter(**dept_filter(request.user))

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(coupon_id__icontains=q) |
            Q(verification_code__icontains=q) |
            Q(vehicle__plate_number__icontains=q) |
            Q(driver__full_name__icontains=q)
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
    fuel_stations = Vendor.objects.filter(type=Vendor.TYPE_FUEL, is_active=True).order_by("name")

    preselect_vehicle = request.GET.get("vehicle", "")

    if request.method == "POST":
        errors = {}
        vehicle_id     = request.POST.get("vehicle", "")
        driver_id      = request.POST.get("driver", "")
        station_id     = request.POST.get("fuel_station", "")
        litres_raw     = request.POST.get("litres", "").strip()
        cost_raw       = request.POST.get("cost_per_litre", "").strip()
        expiry_date    = request.POST.get("expiry_date", "").strip()
        purpose        = request.POST.get("purpose", "").strip()

        if not vehicle_id:  errors["vehicle"]        = "Vehicle is required."
        if not driver_id:   errors["driver"]         = "Driver is required."
        if not station_id:  errors["fuel_station"]   = "Fuel station is required."
        if not litres_raw:  errors["litres"]         = "Litres is required."
        if not cost_raw:    errors["cost_per_litre"] = "Cost per litre is required."

        # Convert to Decimal safely
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
                vehicle_id      = vehicle_id,
                driver_id       = driver_id,
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
                detail=f"Issued coupon {coupon.coupon_id} for {coupon.vehicle.plate_number}"
            )
            messages.success(request, f"Coupon {coupon.coupon_id} issued successfully.")
            return redirect("coupons:print_slip", pk=coupon.pk)

        return render(request, "coupons/form.html", {
            "errors": errors,
            "vehicles": vehicles,
            "drivers": drivers,
            "fuel_stations": fuel_stations,
            "post": request.POST,
        })

    return render(request, "coupons/form.html", {
        "vehicles": vehicles,
        "drivers": drivers,
        "fuel_stations": fuel_stations,
        "preselect_vehicle": preselect_vehicle,
        "post": {},
    })


@login_required
def detail_view(request, pk):
    if not request.user.has_module_perm("coupons", "read"):
        return HttpResponseForbidden()

    coupon = get_object_or_404(FuelCoupon, pk=pk, **dept_filter(request.user))

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "cancel":
            if not request.user.has_module_perm("coupons", "edit"):
                return HttpResponseForbidden()
            reason = request.POST.get("cancel_reason", "").strip()
            if not reason:
                messages.error(request, "A cancellation reason is required.")
            elif coupon.status != FuelCoupon.STATUS_ISSUED:
                messages.error(request, "Only issued coupons can be cancelled.")
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
        "can_edit":   request.user.has_module_perm("coupons", "edit"),
        "can_redeem": request.user.has_module_perm("fuel_logs", "write"),
    })


@login_required
def print_slip(request, pk):
    coupon = get_object_or_404(FuelCoupon, pk=pk, **dept_filter(request.user))
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
    if coupon.status != FuelCoupon.STATUS_ISSUED:
        return JsonResponse({"error": f"Coupon is {coupon.get_status_display()} and cannot be redeemed."})
    if coupon.is_expired_by_date:
        return JsonResponse({"error": "This coupon has expired. Please cancel it and issue a new one."})

    return JsonResponse({
        "id":          coupon.pk,
        "coupon_id":   coupon.coupon_id,
        "plate":       coupon.vehicle.plate_number,
        "driver":      coupon.driver.full_name,
        "station":     coupon.fuel_station.name,
        "station_id":  coupon.fuel_station_id,
        "litres":      str(coupon.litres),
        "total_value": str(coupon.total_value),
        "purpose":     coupon.purpose,
    })
