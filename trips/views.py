from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q, Sum
from django.db import transaction

from .models import Trip, Destination
from drivers.models import Driver
from vehicles.models import Vehicle
from coupons.models import FuelCoupon
from audit.models import AuditLog


def dept_filter(user):
    if user.is_system_admin or not user.department:
        return {}
    return {"vehicle__department": user.department}


# ─────────────────────────────────────────────────────────────
#  TRIPS
# ─────────────────────────────────────────────────────────────
@login_required
def list_view(request):
    if not request.user.has_module_perm("trips", "read"):
        return HttpResponseForbidden()

    qs = Trip.objects.select_related(
        "driver", "vehicle", "from_destination", "to_destination", "logged_by"
    ).filter(**dept_filter(request.user))

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(driver__full_name__icontains=q)
            | Q(vehicle__plate_number__icontains=q)
            | Q(from_destination__name__icontains=q)
            | Q(to_destination__name__icontains=q)
            | Q(from_other__icontains=q)
            | Q(to_other__icontains=q)
            | Q(purpose__icontains=q)
        )

    driver_id = request.GET.get("driver", "")
    if driver_id:
        qs = qs.filter(driver_id=driver_id)

    date_from = request.GET.get("date_from", "")
    date_to   = request.GET.get("date_to", "")
    if date_from:
        qs = qs.filter(trip_date__gte=date_from)
    if date_to:
        qs = qs.filter(trip_date__lte=date_to)

    total_paid = qs.aggregate(s=Sum("amount_paid"))["s"] or Decimal("0.00")

    drivers = Driver.objects.filter(status=Driver.STATUS_ACTIVE).order_by("full_name")

    return render(request, "trips/list.html", {
        "trips": qs[:200],
        "total_paid": total_paid,
        "q": q,
        "drivers": drivers,
        "filters": {
            "driver": driver_id,
            "date_from": date_from,
            "date_to": date_to,
        },
        "can_write": request.user.has_module_perm("trips", "write"),
        "can_edit":  request.user.has_module_perm("trips", "edit"),
    })


@login_required
def create_view(request):
    if not request.user.has_module_perm("trips", "write"):
        return HttpResponseForbidden()

    dept_q = {} if request.user.is_system_admin or not request.user.department else {"department": request.user.department}
    drivers      = Driver.objects.filter(status=Driver.STATUS_ACTIVE).order_by("full_name")
    vehicles     = Vehicle.objects.filter(**dept_q).select_related("default_driver").order_by("plate_number")
    destinations = Destination.objects.filter(is_active=True).order_by("name")

    # ── Correction #2: driver → vehicle suggestion ─────────────────────
    # For each driver, find the vehicle(s) where they're the default driver.
    # If exactly one match, JS will preselect it. If zero or multiple, user picks.
    driver_to_vehicles = {}  # {driver_id: [vehicle_id, ...]}
    for v in vehicles:
        if v.default_driver_id:
            driver_to_vehicles.setdefault(v.default_driver_id, []).append(v.pk)

    # ── Correction #3: per-vehicle coupon list, redeemed only, not yet trip-linked ──
    # A coupon must be redeemed (driver actually picked up the fuel) before it
    # can be linked to a trip. Excludes pending/approved/issued/cancelled/rejected.
    # Trips are vehicle-only, so generator coupons are also excluded.
    eligible_coupons = (
        FuelCoupon.objects
        .filter(
            status=FuelCoupon.STATUS_REDEEMED,
            trips__isnull=True,         # not yet linked to any trip
            vehicle__isnull=False,      # exclude generator coupons
            **dept_filter(request.user),
        )
        .select_related("vehicle", "driver")
        .order_by("-issue_datetime")
    )

    coupons_by_vehicle = {}  # {vehicle_id: [{coupon dict}, ...]}
    for c in eligible_coupons:
        coupons_by_vehicle.setdefault(c.vehicle_id, []).append({
            "id":          c.pk,
            "coupon_id":   c.coupon_id,
            "litres":      str(c.litres),
            "total_value": str(c.total_value),
            "driver":      c.driver.full_name if c.driver_id else "—",
            "status":      c.get_status_display(),
            "issued":      c.issue_datetime.strftime("%d %b %Y"),
        })

    if request.method == "POST":
        errors = {}
        driver_id   = request.POST.get("driver", "")
        vehicle_id  = request.POST.get("vehicle", "")
        from_dest   = request.POST.get("from_destination", "")
        from_other  = request.POST.get("from_other", "").strip()
        to_dest     = request.POST.get("to_destination", "")
        to_other    = request.POST.get("to_other", "").strip()
        trip_date   = request.POST.get("trip_date", "").strip()
        amount_raw  = request.POST.get("amount_paid", "").strip()
        purpose     = request.POST.get("purpose", "").strip()
        notes       = request.POST.get("notes", "").strip()
        coupon_ids  = request.POST.getlist("fuel_coupons")

        if not driver_id:  errors["driver"]      = "Driver is required."
        if not vehicle_id: errors["vehicle"]     = "Vehicle is required."
        if not trip_date:  errors["trip_date"]   = "Trip date is required."
        if not amount_raw: errors["amount_paid"] = "Amount paid is required."

        if not from_dest and not from_other:
            errors["from"] = "Select an origin or enter a one-off."
        if not to_dest and not to_other:
            errors["to"] = "Select a destination or enter a one-off."

        amount = None
        if amount_raw:
            try:
                amount = Decimal(amount_raw)
                if amount < 0:
                    errors["amount_paid"] = "Amount cannot be negative."
            except InvalidOperation:
                errors["amount_paid"] = "Enter a valid number."

        if not errors:
            with transaction.atomic():
                trip = Trip.objects.create(
                    driver_id          = driver_id,
                    vehicle_id         = vehicle_id,
                    from_destination_id= from_dest or None,
                    from_other         = "" if from_dest else from_other,
                    to_destination_id  = to_dest or None,
                    to_other           = "" if to_dest else to_other,
                    trip_date          = trip_date,
                    amount_paid        = amount,
                    purpose            = purpose,
                    notes              = notes,
                    logged_by          = request.user,
                )
                if coupon_ids:
                    trip.fuel_coupons.set(coupon_ids)

            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="trips",
                record_id=str(trip.pk),
                detail=f"Logged trip for {trip.driver.full_name}: {trip.from_label} → {trip.to_label}, ₦{trip.amount_paid}"
            )
            messages.success(request, f"Trip logged for {trip.driver.full_name}.")
            return redirect("trips:list")

        return render(request, "trips/form.html", {
            "errors": errors, "post": request.POST,
            "drivers": drivers, "vehicles": vehicles, "destinations": destinations,
            "coupons_by_vehicle": coupons_by_vehicle,
            "driver_to_vehicles": driver_to_vehicles,
            "selected_coupons": coupon_ids,
        })

    return render(request, "trips/form.html", {
        "drivers": drivers, "vehicles": vehicles, "destinations": destinations,
        "coupons_by_vehicle": coupons_by_vehicle,
        "driver_to_vehicles": driver_to_vehicles,
        "selected_coupons": [],
    })


@login_required
def detail_view(request, pk):
    if not request.user.has_module_perm("trips", "read"):
        return HttpResponseForbidden()
    trip = get_object_or_404(
        Trip.objects.select_related("driver", "vehicle", "from_destination", "to_destination", "logged_by")
                    .prefetch_related("fuel_coupons"),
        pk=pk, **dept_filter(request.user)
    )
    return render(request, "trips/detail.html", {
        "trip": trip,
        "can_edit": request.user.has_module_perm("trips", "edit"),
    })


# ─────────────────────────────────────────────────────────────
#  DESTINATIONS
# ─────────────────────────────────────────────────────────────
@login_required
def destination_list(request):
    if not request.user.has_module_perm("destinations", "read"):
        return HttpResponseForbidden()
    qs = Destination.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
    return render(request, "destinations/list.html", {
        "destinations": qs,
        "q": q,
        "can_write": request.user.has_module_perm("destinations", "write"),
        "can_edit":  request.user.has_module_perm("destinations", "edit"),
    })


@login_required
def destination_create(request):
    if not request.user.has_module_perm("destinations", "write"):
        return HttpResponseForbidden()
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        notes = request.POST.get("notes", "").strip()
        is_active = request.POST.get("is_active") == "on"
        errors = {}
        if not name:
            errors["name"] = "Name is required."
        elif Destination.objects.filter(name__iexact=name).exists():
            errors["name"] = "A destination with that name already exists."
        if not errors:
            d = Destination.objects.create(
                name=name, code=code, notes=notes, is_active=is_active,
                created_by=request.user,
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="destinations",
                record_id=str(d.pk), detail=f"Created destination '{d.name}'"
            )
            messages.success(request, f"Destination '{d.name}' added.")
            return redirect("trips:destination_list")
        return render(request, "destinations/form.html", {"errors": errors, "post": request.POST})
    return render(request, "destinations/form.html", {})


@login_required
def destination_edit(request, pk):
    if not request.user.has_module_perm("destinations", "edit"):
        return HttpResponseForbidden()
    d = get_object_or_404(Destination, pk=pk)
    if request.method == "POST":
        d.name = request.POST.get("name", "").strip() or d.name
        d.code = request.POST.get("code", "").strip()
        d.notes = request.POST.get("notes", "").strip()
        d.is_active = request.POST.get("is_active") == "on"
        d.save()
        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_EDIT, module="destinations",
            record_id=str(d.pk), detail=f"Edited destination '{d.name}'"
        )
        messages.success(request, "Destination updated.")
        return redirect("trips:destination_list")
    return render(request, "destinations/form.html", {"destination": d, "post": {}})
