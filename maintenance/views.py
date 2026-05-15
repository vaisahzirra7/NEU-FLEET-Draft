from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q, Sum
from django.db import transaction
from .models import MaintenanceRecord, MaintenanceItem, SERVICE_APPLIES_TO
from vehicles.models import Vehicle
from generators.models import Generator
from vendors.models import Vendor
from audit.models import AuditLog


def _service_choices_with_meta():
    """
    Returns [(value, label, applies_to_csv)] for the maintenance form.
    The applies_to_csv string becomes a data-attribute on each <option>
    so JS can hide/show options based on the selected asset type.
    """
    return [
        (val, label, ",".join(SERVICE_APPLIES_TO.get(val, ("vehicle", "generator"))))
        for val, label in MaintenanceRecord.SERVICE_CHOICES
    ]


def dept_filter(user):
    """
    Department scoping for maintenance records.

    Vehicle records are filtered to the user's department via vehicle.department.
    Generator records are NOT department-scoped (generators are organisation-wide),
    so all generator maintenance records are visible to any user with the
    maintenance read permission.

    Returns a Q object — callers use `qs.filter(dept_filter(request.user))`.
    """
    if user.is_system_admin or not user.department:
        return Q()
    return Q(generator__isnull=False) | Q(vehicle__department=user.department)


@login_required
def list_view(request):
    if not request.user.has_module_perm("maintenance", "read"):
        return HttpResponseForbidden()

    qs = MaintenanceRecord.objects.select_related(
        "vehicle", "generator", "vendor", "created_by"
    ).prefetch_related("items").filter(dept_filter(request.user))

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(vehicle__plate_number__icontains=q) |
            Q(generator__tag__icontains=q) |
            Q(generator__name__icontains=q) |
            Q(description__icontains=q) |
            Q(vendor__name__icontains=q) |
            Q(vendor_other__icontains=q) |
            Q(items__description__icontains=q)
        ).distinct()

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
        "can_edit":  request.user.has_module_perm("maintenance", "edit"),
    })


@login_required
def create_view(request):
    if not request.user.has_module_perm("maintenance", "write"):
        return HttpResponseForbidden()

    dept_q     = {} if request.user.is_system_admin or not request.user.department else {"department": request.user.department}
    vehicles   = Vehicle.objects.filter(**dept_q).order_by("plate_number")
    generators = Generator.objects.filter(status=Generator.STATUS_ACTIVE).order_by("tag")
    vendors    = Vendor.objects.filter(is_active=True).exclude(type=Vendor.TYPE_FUEL).order_by("name")

    preselect_vehicle   = request.GET.get("vehicle", "")
    preselect_generator = request.GET.get("generator", "")
    default_asset_type  = "generator" if preselect_generator else "vehicle"

    if request.method == "POST":
        errors = {}
        asset_type   = request.POST.get("asset_type", "vehicle").strip()
        vehicle_id   = request.POST.get("vehicle", "")
        generator_id = request.POST.get("generator", "")
        service_date = request.POST.get("service_date", "").strip()
        approved_by  = request.POST.get("approved_by", "").strip()
        description  = request.POST.get("description", "").strip()

        # Asset validation
        if asset_type == "generator":
            if not generator_id: errors["generator"] = "Generator is required."
            vehicle_id = ""  # force-clear stray
        else:
            asset_type = "vehicle"
            if not vehicle_id: errors["vehicle"] = "Vehicle is required."
            generator_id = ""

        if not service_date: errors["service_date"] = "Service date is required."
        if not approved_by:  errors["approved_by"]  = "Approved by is required."

        # ── Parse line items (unchanged from Stage 3) ──
        item_types = request.POST.getlist("item_service_type")
        item_descs = request.POST.getlist("item_description")
        item_costs = request.POST.getlist("item_cost")

        n = max(len(item_types), len(item_descs), len(item_costs))
        item_types += [""] * (n - len(item_types))
        item_descs += [""] * (n - len(item_descs))
        item_costs += [""] * (n - len(item_costs))

        parsed_items = []
        item_errors  = []
        for i, (stype, sdesc, scost) in enumerate(zip(item_types, item_descs, item_costs)):
            stype = (stype or "").strip()
            sdesc = (sdesc or "").strip()
            scost = (scost or "").strip()

            if not stype and not sdesc and not scost:
                item_errors.append({})
                continue

            row_err = {}
            if not stype: row_err["service_type"] = "Required"
            if not sdesc: row_err["description"]  = "Required"
            cost_val = None
            if not scost:
                row_err["cost"] = "Required"
            else:
                try:
                    cost_val = Decimal(scost)
                    if cost_val < 0:
                        row_err["cost"] = "Cannot be negative"
                except InvalidOperation:
                    row_err["cost"] = "Enter a valid number"

            item_errors.append(row_err)
            if not row_err:
                parsed_items.append({
                    "service_type": stype,
                    "description":  sdesc,
                    "cost":         cost_val,
                })

        if not parsed_items and not any(item_errors):
            errors["items"] = "Add at least one line item."
        elif any(item_errors):
            errors["items"] = "Fix the line items below."

        if not errors:
            with transaction.atomic():
                rec = MaintenanceRecord.objects.create(
                    vehicle_id        = vehicle_id   or None,
                    generator_id      = generator_id or None,
                    service_date      = service_date,
                    description       = description,
                    vendor_id         = request.POST.get("vendor") or None,
                    vendor_other      = request.POST.get("vendor_other", "").strip(),
                    next_service_date = request.POST.get("next_service_date") or None,
                    approved_by       = approved_by,
                    notes             = request.POST.get("notes", "").strip(),
                    created_by        = request.user,
                )
                for it in parsed_items:
                    MaintenanceItem.objects.create(
                        record       = rec,
                        service_type = it["service_type"],
                        description  = it["description"],
                        cost         = it["cost"],
                    )
                rec.refresh_from_db()

            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="maintenance",
                record_id=str(rec.pk),
                detail=(
                    f"Logged maintenance for {rec.asset_label}: "
                    f"{len(parsed_items)} item{'s' if len(parsed_items) != 1 else ''}, "
                    f"total ₦{rec.total_cost}"
                ),
            )
            messages.success(
                request,
                f"Maintenance record logged for {rec.asset_label} "
                f"({len(parsed_items)} item{'s' if len(parsed_items) != 1 else ''}, total ₦{rec.total_cost})."
            )
            # Redirect to whichever asset detail page applies
            if rec.is_for_vehicle:
                return redirect("vehicles:detail", pk=rec.vehicle_id)
            return redirect("generators:detail", pk=rec.generator_id)

        submitted_rows = list(zip(item_types, item_descs, item_costs, item_errors))
        return render(request, "maintenance/form.html", {
            "errors": errors,
            "item_errors": item_errors,
            "submitted_rows": submitted_rows,
            "post": request.POST,
            "vehicles": vehicles, "generators": generators, "vendors": vendors,
            "service_choices": _service_choices_with_meta(),
            "default_asset_type": asset_type,
        })

    return render(request, "maintenance/form.html", {
        "vehicles": vehicles, "generators": generators, "vendors": vendors,
        "service_choices": _service_choices_with_meta(),
        "preselect_vehicle":   preselect_vehicle,
        "preselect_generator": preselect_generator,
        "default_asset_type":  default_asset_type,
        "submitted_rows": [],
    })


@login_required
def detail_view(request, pk):
    if not request.user.has_module_perm("maintenance", "read"):
        return HttpResponseForbidden()
    rec = get_object_or_404(
        MaintenanceRecord.objects.select_related("vehicle", "generator", "vendor", "created_by"),
        dept_filter(request.user), pk=pk
    )
    return render(request, "maintenance/detail.html", {
        "rec": rec,
        "can_edit": request.user.has_module_perm("maintenance", "edit"),
    })
