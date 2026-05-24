from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q, Sum
from .models import Vendor
from audit.models import AuditLog


@login_required
def detail_view(request, pk):
    """
    Vendor detail page. Especially useful for fuel stations where it shows
    the deposit/coupon ledger and current balance.

    For non-fuel-station vendors, shows basic spend summary.
    """
    if not request.user.has_module_perm("vendors", "read"):
        return HttpResponseForbidden()

    vendor = get_object_or_404(Vendor, pk=pk)

    # Common: spend summary across all vendor types
    from fuel_logs.models import FuelLog
    from maintenance.models import MaintenanceRecord
    fuel_spend  = FuelLog.objects.filter(fuel_station=vendor).aggregate(t=Sum("actual_cost"))["t"] or 0
    maint_spend = MaintenanceRecord.objects.filter(vendor=vendor).aggregate(t=Sum("total_cost"))["t"] or 0

    ctx = {
        "obj":          vendor,
        "fuel_spend":   fuel_spend,
        "maint_spend":  maint_spend,
        "total_spend":  fuel_spend + maint_spend,
        "can_edit":     request.user.has_module_perm("vendors", "edit"),
    }

    # Fuel-station-specific: deposit and coupon ledger
    if vendor.type == Vendor.TYPE_FUEL:
        from coupons.models import FuelCoupon

        # Deposit history (with filters)
        deposits_qs = vendor.deposits.select_related("created_by")

        date_from = request.GET.get("date_from", "").strip()
        date_to   = request.GET.get("date_to", "").strip()
        if date_from:
            deposits_qs = deposits_qs.filter(deposit_date__gte=date_from)
        if date_to:
            deposits_qs = deposits_qs.filter(deposit_date__lte=date_to)

        # Coupon history at this station (with same date filter applied
        # to issue_datetime so totals at the bottom line up)
        coupons_qs = FuelCoupon.objects.filter(fuel_station=vendor).select_related(
            "vehicle", "generator", "driver", "issued_by", "approved_by"
        )
        if date_from:
            coupons_qs = coupons_qs.filter(issue_datetime__date__gte=date_from)
        if date_to:
            coupons_qs = coupons_qs.filter(issue_datetime__date__lte=date_to)

        ctx.update({
            "deposits":           deposits_qs[:100],
            "coupons":            coupons_qs.order_by("-issue_datetime")[:100],
            "filter_date_from":   date_from,
            "filter_date_to":     date_to,
            "can_record_deposit": request.user.has_module_perm("station_deposits", "write"),
            "can_delete_deposit": request.user.is_system_admin,
        })

    return render(request, "vendors/detail.html", ctx)



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
