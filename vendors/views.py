from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q, Sum
from .models import Vendor
from audit.models import AuditLog


@login_required
def list_view(request):
    if not request.user.has_module_perm("vendors", "read"):
        return HttpResponseForbidden()

    qs = Vendor.objects.all()

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(address__icontains=q))

    vtype = request.GET.get("type", "")
    if vtype:
        qs = qs.filter(type=vtype)

    active_only = request.GET.get("active", "")
    if active_only == "1":
        qs = qs.filter(is_active=True)
    elif active_only == "0":
        qs = qs.filter(is_active=False)

    return render(request, "vendors/list.html", {
        "vendors": qs,
        "q": q,
        "type_filter": vtype,
        "active_only": active_only,
        "type_choices": Vendor.TYPE_CHOICES,
        "can_write":  request.user.has_module_perm("vendors", "write"),
        "can_edit":   request.user.has_module_perm("vendors", "edit"),
        "can_delete": request.user.has_module_perm("vendors", "delete"),
    })


@login_required
def create_view(request):
    if not request.user.has_module_perm("vendors", "write"):
        return HttpResponseForbidden()

    if request.method == "POST":
        errors = {}
        name = request.POST.get("name", "").strip()
        if not name:
            errors["name"] = "Vendor name is required."
        elif Vendor.objects.filter(name__iexact=name).exists():
            errors["name"] = "A vendor with this name already exists."
        if not request.POST.get("type"):
            errors["type"] = "Vendor type is required."

        if not errors:
            v = Vendor.objects.create(
                name    = name,
                type    = request.POST["type"],
                phone   = request.POST.get("phone", "").strip(),
                address = request.POST.get("address", "").strip(),
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="vendors",
                record_id=str(v.pk), detail=f"Added vendor {v.name}"
            )
            messages.success(request, f"Vendor '{v.name}' added successfully.")
            return redirect("vendors:list")

        return render(request, "vendors/form.html", {
            "errors": errors,
            "name_val":    request.POST.get("name", ""),
            "type_val":    request.POST.get("type", ""),
            "phone_val":   request.POST.get("phone", ""),
            "address_val": request.POST.get("address", ""),
            "type_choices": Vendor.TYPE_CHOICES,
        })

    return render(request, "vendors/form.html", {"type_choices": Vendor.TYPE_CHOICES})


@login_required
def delete_view(request, pk):
    if not request.user.has_module_perm("vendors", "delete"):
        return HttpResponseForbidden()

    vendor = get_object_or_404(Vendor, pk=pk)

    # Safety check — block delete if vendor has any linked records
    from fuel_logs.models import FuelLog
    from maintenance.models import MaintenanceRecord
    fuel_count  = FuelLog.objects.filter(fuel_station=vendor).count()
    maint_count = MaintenanceRecord.objects.filter(vendor=vendor).count()

    if request.method == "POST":
        if fuel_count or maint_count:
            messages.error(request, f"Cannot delete '{vendor.name}' — it has {fuel_count} fuel log(s) and {maint_count} maintenance record(s) linked to it. Deactivate it instead.")
            return redirect("vendors:list")

        name = vendor.name
        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_DELETE, module="vendors",
            record_id=str(vendor.pk), detail=f"Deleted vendor {name}"
        )
        vendor.delete()
        messages.success(request, f"Vendor '{name}' deleted.")
        return redirect("vendors:list")

    return render(request, "vendors/confirm_delete.html", {
        "vendor": vendor,
        "fuel_count": fuel_count,
        "maint_count": maint_count,
        "has_records": bool(fuel_count or maint_count),
    })
    if not request.user.has_module_perm("vendors", "edit"):
        return HttpResponseForbidden()

    vendor = get_object_or_404(Vendor, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action", "save")

        # Toggle active/inactive
        if action == "toggle_active":
            vendor.is_active = not vendor.is_active
            vendor.save(update_fields=["is_active", "updated_at"])
            state = "activated" if vendor.is_active else "deactivated"
            messages.success(request, f"Vendor '{vendor.name}' {state}.")
            return redirect("vendors:list")

        # Save changes (action == "save" or no action)
        vendor.name    = request.POST.get("name", vendor.name).strip()
        vendor.type    = request.POST.get("type", vendor.type)
        vendor.phone   = request.POST.get("phone", "").strip()
        vendor.address = request.POST.get("address", "").strip()
        vendor.save()

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_EDIT, module="vendors",
            record_id=str(vendor.pk), detail=f"Updated vendor {vendor.name}"
        )
        messages.success(request, f"Vendor '{vendor.name}' updated.")
        return redirect("vendors:list")

    # Spend summary
    from fuel_logs.models import FuelLog
    from maintenance.models import MaintenanceRecord
    fuel_spend  = FuelLog.objects.filter(fuel_station=vendor).aggregate(t=Sum("actual_cost"))["t"] or 0
    maint_spend = MaintenanceRecord.objects.filter(vendor=vendor).aggregate(t=Sum("total_cost"))["t"] or 0

    return render(request, "vendors/form.html", {
        "obj": vendor,
        "type_choices": Vendor.TYPE_CHOICES,
        "fuel_spend": fuel_spend,
        "maint_spend": maint_spend,
        "total_spend": fuel_spend + maint_spend,
    })


@login_required
def edit_view(request, pk):
    if not request.user.has_module_perm("vendors", "edit"):
        return HttpResponseForbidden()

    vendor = get_object_or_404(Vendor, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action", "save")

        # Toggle active/inactive
        if action == "toggle_active":
            vendor.is_active = not vendor.is_active
            vendor.save(update_fields=["is_active", "updated_at"])
            state = "activated" if vendor.is_active else "deactivated"
            messages.success(request, f"Vendor '{vendor.name}' {state}.")
            return redirect("vendors:list")

        vendor.name    = request.POST.get("name", vendor.name).strip()
        vendor.type    = request.POST.get("type", vendor.type)
        vendor.phone   = request.POST.get("phone", "").strip()
        vendor.address = request.POST.get("address", "").strip()
        vendor.save()

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_EDIT, module="vendors",
            record_id=str(vendor.pk), detail=f"Updated vendor {vendor.name}"
        )
        messages.success(request, f"Vendor '{vendor.name}' updated.")
        return redirect("vendors:list")

    # Spend summary
    from fuel_logs.models import FuelLog
    from maintenance.models import MaintenanceRecord
    fuel_spend  = FuelLog.objects.filter(fuel_station=vendor).aggregate(t=Sum("total_cost" if False else "actual_cost"))["t"] or 0
    maint_spend = MaintenanceRecord.objects.filter(vendor=vendor).aggregate(t=Sum("total_cost"))["t"] or 0

    return render(request, "vendors/form.html", {
        "obj": vendor,
        "type_choices": Vendor.TYPE_CHOICES,
        "fuel_spend": fuel_spend,
        "maint_spend": maint_spend,
        "total_spend": fuel_spend + maint_spend,
    })
