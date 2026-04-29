from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q, Sum
from .models import MaintenanceRecord
from vehicles.models import Vehicle
from vendors.models import Vendor
from audit.models import AuditLog


def dept_filter(user):
    if user.is_system_admin or not user.department:
        return {}
    return {"vehicle__department": user.department}


@login_required
def list_view(request):
    if not request.user.has_module_perm("maintenance", "read"):
        return HttpResponseForbidden()

    qs = MaintenanceRecord.objects.select_related(
        "vehicle", "vendor", "created_by"
    ).filter(**dept_filter(request.user))

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(vehicle__plate_number__icontains=q) |
            Q(description__icontains=q) |
            Q(vendor__name__icontains=q) |
            Q(vendor_other__icontains=q)
        )

    service_type = request.GET.get("type", "")
    if service_type:
        qs = qs.filter(service_type=service_type)

    vehicle_id = request.GET.get("vehicle", "")
    if vehicle_id:
        qs = qs.filter(vehicle_id=vehicle_id)

    return render(request, "maintenance/list.html", {
        "records": qs[:100],
        "q": q,
        "type_filter": service_type,
        "service_choices": MaintenanceRecord.SERVICE_CHOICES,
        "can_write": request.user.has_module_perm("maintenance", "write"),
    })


@login_required
def create_view(request):
    if not request.user.has_module_perm("maintenance", "write"):
        return HttpResponseForbidden()

    dept_q = {} if request.user.is_system_admin or not request.user.department else {"department": request.user.department}
    vehicles = Vehicle.objects.filter(**dept_q).order_by("plate_number")
    vendors  = Vendor.objects.filter(is_active=True).exclude(type=Vendor.TYPE_FUEL).order_by("name")

    preselect_vehicle = request.GET.get("vehicle", "")

    if request.method == "POST":
        errors = {}
        vehicle_id   = request.POST.get("vehicle", "")
        service_date = request.POST.get("service_date", "").strip()
        service_type = request.POST.get("service_type", "")
        description  = request.POST.get("description", "").strip()
        total_cost   = request.POST.get("total_cost", "").strip()
        approved_by  = request.POST.get("approved_by", "").strip()

        if not vehicle_id:   errors["vehicle"]      = "Vehicle is required."
        if not service_date: errors["service_date"] = "Service date is required."
        if not service_type: errors["service_type"] = "Service type is required."
        if not description:  errors["description"]  = "Description is required."
        if not total_cost:   errors["total_cost"]   = "Total cost is required."
        if not approved_by:  errors["approved_by"]  = "Approved by is required."

        if not errors:
            rec = MaintenanceRecord.objects.create(
                vehicle_id       = vehicle_id,
                service_date     = service_date,
                service_type     = service_type,
                description      = description,
                vendor_id        = request.POST.get("vendor") or None,
                vendor_other     = request.POST.get("vendor_other", "").strip(),
                total_cost       = total_cost,
                next_service_date= request.POST.get("next_service_date") or None,
                approved_by      = approved_by,
                notes            = request.POST.get("notes", "").strip(),
                created_by       = request.user,
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="maintenance",
                record_id=str(rec.pk),
                detail=f"Logged {rec.get_service_type_display()} for {rec.vehicle.plate_number}"
            )
            messages.success(request, f"Maintenance record logged for {rec.vehicle.plate_number}.")
            return redirect("vehicles:detail", pk=rec.vehicle.pk)

        return render(request, "maintenance/form.html", {
            "errors": errors, "post": request.POST,
            "vehicles": vehicles, "vendors": vendors,
            "service_choices": MaintenanceRecord.SERVICE_CHOICES,
        })

    return render(request, "maintenance/form.html", {
        "vehicles": vehicles, "vendors": vendors,
        "service_choices": MaintenanceRecord.SERVICE_CHOICES,
        "preselect_vehicle": preselect_vehicle,
    })



@login_required
def detail_view(request, pk):
    if not request.user.has_module_perm("maintenance", "read"):
        return HttpResponseForbidden()
    rec = get_object_or_404(MaintenanceRecord, pk=pk, **dept_filter(request.user))
    return render(request, "maintenance/detail.html", {"rec": rec})
