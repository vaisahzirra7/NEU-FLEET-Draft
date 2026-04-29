from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q, Sum
from .models import Vehicle
from drivers.models import Driver
from accounts.models import Department
from audit.models import AuditLog


def dept_filter(user):
    """Returns a dict to filter querysets by department for non-admins."""
    if user.is_system_admin or not user.department:
        return {}
    return {"department": user.department}


@login_required
def list_view(request):
    if not request.user.has_module_perm("vehicles", "read"):
        return HttpResponseForbidden()

    qs = Vehicle.objects.select_related("department", "default_driver").filter(
        **dept_filter(request.user)
    )

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(plate_number__icontains=q) |
            Q(make__icontains=q) |
            Q(model__icontains=q)
        )

    # Filter by status
    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)

    # Filter by type
    vtype = request.GET.get("type", "")
    if vtype:
        qs = qs.filter(vehicle_type=vtype)

    return render(request, "vehicles/list.html", {
        "vehicles": qs,
        "q": q,
        "status_filter": status,
        "type_filter": vtype,
        "status_choices": Vehicle.STATUS_CHOICES,
        "type_choices": Vehicle.TYPE_CHOICES,
        "can_write": request.user.has_module_perm("vehicles", "write"),
    })


@login_required
def detail_view(request, pk):
    if not request.user.has_module_perm("vehicles", "read"):
        return HttpResponseForbidden()

    vehicle = get_object_or_404(Vehicle, pk=pk, **dept_filter(request.user))

    # Recent fuel logs
    from fuel_logs.models import FuelLog
    from maintenance.models import MaintenanceRecord
    from coupons.models import FuelCoupon

    fuel_logs     = FuelLog.objects.filter(vehicle=vehicle).select_related("coupon", "logged_by")[:10]
    maintenance   = MaintenanceRecord.objects.filter(vehicle=vehicle).order_by("-service_date")[:10]
    coupons       = FuelCoupon.objects.filter(vehicle=vehicle).order_by("-issue_datetime")[:10]

    # Total spend
    total_fuel  = FuelLog.objects.filter(vehicle=vehicle).aggregate(t=Sum("actual_cost"))["t"] or 0
    total_maint = MaintenanceRecord.objects.filter(vehicle=vehicle).aggregate(t=Sum("total_cost"))["t"] or 0

    return render(request, "vehicles/detail.html", {
        "vehicle": vehicle,
        "fuel_logs": fuel_logs,
        "maintenance": maintenance,
        "coupons": coupons,
        "total_fuel": total_fuel,
        "total_maint": total_maint,
        "total_spend": total_fuel + total_maint,
        "can_edit": request.user.has_module_perm("vehicles", "edit"),
    })


@login_required
def create_view(request):
    if not request.user.has_module_perm("vehicles", "write"):
        return HttpResponseForbidden()

    departments = Department.objects.filter(is_active=True)
    drivers     = Driver.objects.filter(status=Driver.STATUS_ACTIVE)

    if request.method == "POST":
        errors = {}
        plate  = request.POST.get("plate_number", "").strip().upper()
        if not plate:
            errors["plate_number"] = "Plate number is required."
        elif Vehicle.objects.filter(plate_number=plate).exists():
            errors["plate_number"] = "A vehicle with this plate number already exists."
        if not request.POST.get("make"):         errors["make"]         = "Make is required."
        if not request.POST.get("model"):        errors["model"]        = "Model is required."
        if not request.POST.get("year"):         errors["year"]         = "Year is required."
        if not request.POST.get("fuel_type"):    errors["fuel_type"]    = "Fuel type is required."
        if not request.POST.get("vehicle_type"): errors["vehicle_type"] = "Vehicle type is required."
        if not request.POST.get("department"):   errors["department"]   = "Department is required."

        if not errors:
            v = Vehicle.objects.create(
                plate_number      = plate,
                vehicle_type      = request.POST["vehicle_type"],
                make              = request.POST["make"].strip(),
                model             = request.POST["model"].strip(),
                year              = request.POST["year"],
                colour            = request.POST.get("colour", "").strip(),
                engine_no         = request.POST.get("engine_no", "").strip(),
                chassis_no        = request.POST.get("chassis_no", "").strip(),
                fuel_type         = request.POST["fuel_type"],
                department_id     = request.POST["department"],
                default_driver_id = request.POST.get("default_driver") or None,
                status            = request.POST.get("status", Vehicle.STATUS_ACTIVE),
                notes             = request.POST.get("notes", "").strip(),
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="vehicles",
                record_id=str(v.pk), detail=f"Created vehicle {v.plate_number}"
            )
            messages.success(request, f"Vehicle {v.plate_number} registered successfully.")
            return redirect("vehicles:detail", pk=v.pk)

        return render(request, "vehicles/form.html", {
            "errors": errors,
            "post": request.POST.dict(),  # plain dict so template lookups resolve safely
            "departments": departments,
            "drivers": drivers,
            "status_choices": Vehicle.STATUS_CHOICES,
            "type_choices": Vehicle.TYPE_CHOICES,
            "fuel_choices": Vehicle.FUEL_CHOICES,
        })

    # GET — pass an empty dict so template references like
    # {{ post.plate_number }} resolve safely without raising VariableDoesNotExist
    return render(request, "vehicles/form.html", {
        "post": {},
        "departments": departments,
        "drivers": drivers,
        "status_choices": Vehicle.STATUS_CHOICES,
        "type_choices": Vehicle.TYPE_CHOICES,
        "fuel_choices": Vehicle.FUEL_CHOICES,
    })


@login_required
def edit_view(request, pk):
    if not request.user.has_module_perm("vehicles", "edit"):
        return HttpResponseForbidden()

    vehicle     = get_object_or_404(Vehicle, pk=pk, **dept_filter(request.user))
    departments = Department.objects.filter(is_active=True)
    drivers     = Driver.objects.filter(status=Driver.STATUS_ACTIVE)

    if request.method == "POST":
        vehicle.vehicle_type      = request.POST.get("vehicle_type", vehicle.vehicle_type)
        vehicle.make              = request.POST.get("make", vehicle.make).strip()
        vehicle.model             = request.POST.get("model", vehicle.model).strip()
        vehicle.year              = request.POST.get("year", vehicle.year)
        vehicle.colour            = request.POST.get("colour", "").strip()
        vehicle.engine_no         = request.POST.get("engine_no", "").strip()
        vehicle.chassis_no        = request.POST.get("chassis_no", "").strip()
        vehicle.fuel_type         = request.POST.get("fuel_type", vehicle.fuel_type)
        vehicle.department_id     = request.POST.get("department", vehicle.department_id)
        vehicle.default_driver_id = request.POST.get("default_driver") or None
        vehicle.status            = request.POST.get("status", vehicle.status)
        vehicle.notes             = request.POST.get("notes", "").strip()
        vehicle.save()

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_EDIT, module="vehicles",
            record_id=str(vehicle.pk), detail=f"Updated vehicle {vehicle.plate_number}"
        )
        messages.success(request, f"Vehicle {vehicle.plate_number} updated.")
        return redirect("vehicles:detail", pk=vehicle.pk)

    return render(request, "vehicles/form.html", {
        "obj": vehicle,
        "departments": departments,
        "drivers": drivers,
        "status_choices": Vehicle.STATUS_CHOICES,
        "type_choices": Vehicle.TYPE_CHOICES,
        "fuel_choices": Vehicle.FUEL_CHOICES,
    })
