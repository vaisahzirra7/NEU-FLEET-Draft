from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import Generator
from audit.models import AuditLog


@login_required
def list_view(request):
    if not request.user.has_module_perm("generators", "read"):
        return HttpResponseForbidden()

    # Generators are organisation-wide; no department scoping.
    qs = Generator.objects.all()

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(tag__icontains=q)
            | Q(name__icontains=q)
            | Q(make__icontains=q)
            | Q(model__icontains=q)
            | Q(serial_number__icontains=q)
            | Q(building__icontains=q)
        )

    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)

    fuel = request.GET.get("fuel", "")
    if fuel:
        qs = qs.filter(fuel_type=fuel)

    return render(request, "generators/list.html", {
        "generators": qs,
        "q": q,
        "status_filter": status,
        "fuel_filter": fuel,
        "status_choices": Generator.STATUS_CHOICES,
        "fuel_choices": Generator.FUEL_CHOICES,
        "can_write":  request.user.has_module_perm("generators", "write"),
        "can_edit":   request.user.has_module_perm("generators", "edit"),
        "can_delete": request.user.has_module_perm("generators", "delete"),
    })


@login_required
def detail_view(request, pk):
    if not request.user.has_module_perm("generators", "read"):
        return HttpResponseForbidden()
    gen = get_object_or_404(Generator, pk=pk)
    return render(request, "generators/detail.html", {
        "gen": gen,
        "can_edit":   request.user.has_module_perm("generators", "edit"),
        "can_delete": request.user.has_module_perm("generators", "delete"),
    })


def _validate_generator_form(request, instance=None):
    """Shared validation for create + edit. Returns (cleaned_dict, errors_dict)."""
    cleaned = {
        "tag":           request.POST.get("tag", "").strip(),
        "name":          request.POST.get("name", "").strip(),
        "make":          request.POST.get("make", "").strip(),
        "model":         request.POST.get("model", "").strip(),
        "serial_number": request.POST.get("serial_number", "").strip(),
        "kva_rating":    request.POST.get("kva_rating", "").strip(),
        "fuel_type":     request.POST.get("fuel_type", "").strip(),
        "tank_capacity_litres": request.POST.get("tank_capacity_litres", "").strip(),
        "building":      request.POST.get("building", "").strip(),
        "location_note": request.POST.get("location_note", "").strip(),
        "status":        request.POST.get("status", Generator.STATUS_ACTIVE),
        "installed_date": request.POST.get("installed_date", "").strip() or None,
        "needs_monthly_fuel": request.POST.get("needs_monthly_fuel") == "on",
        "notes":         request.POST.get("notes", "").strip(),
    }
    errors = {}

    if not cleaned["tag"]:
        errors["tag"] = "Tag is required."
    else:
        # Unique-tag check
        existing = Generator.objects.filter(tag__iexact=cleaned["tag"])
        if instance:
            existing = existing.exclude(pk=instance.pk)
        if existing.exists():
            errors["tag"] = "Another generator already uses this tag."

    if not cleaned["name"]:        errors["name"]          = "Name is required."
    if not cleaned["make"]:        errors["make"]          = "Make is required."
    if not cleaned["building"]:    errors["building"]      = "Building is required."

    # kva_rating
    if not cleaned["kva_rating"]:
        errors["kva_rating"] = "kVA rating is required."
    else:
        try:
            cleaned["kva_rating"] = Decimal(cleaned["kva_rating"])
            if cleaned["kva_rating"] <= 0:
                errors["kva_rating"] = "kVA rating must be greater than zero."
        except InvalidOperation:
            errors["kva_rating"] = "Enter a valid number for kVA rating."

    # tank_capacity_litres (optional)
    if cleaned["tank_capacity_litres"]:
        try:
            cleaned["tank_capacity_litres"] = Decimal(cleaned["tank_capacity_litres"])
            if cleaned["tank_capacity_litres"] <= 0:
                errors["tank_capacity_litres"] = "Tank capacity must be greater than zero."
        except InvalidOperation:
            errors["tank_capacity_litres"] = "Enter a valid number for tank capacity."
    else:
        cleaned["tank_capacity_litres"] = None

    # fuel_type — fall back to diesel if blank
    if cleaned["fuel_type"] not in dict(Generator.FUEL_CHOICES):
        cleaned["fuel_type"] = Generator.FUEL_DIESEL

    # status — fall back to active if blank
    if cleaned["status"] not in dict(Generator.STATUS_CHOICES):
        cleaned["status"] = Generator.STATUS_ACTIVE

    return cleaned, errors


@login_required
def create_view(request):
    if not request.user.has_module_perm("generators", "write"):
        return HttpResponseForbidden()

    if request.method == "POST":
        cleaned, errors = _validate_generator_form(request)

        if not errors:
            gen = Generator.objects.create(
                tag                  = cleaned["tag"],
                name                 = cleaned["name"],
                make                 = cleaned["make"],
                model                = cleaned["model"],
                serial_number        = cleaned["serial_number"],
                kva_rating           = cleaned["kva_rating"],
                fuel_type            = cleaned["fuel_type"],
                tank_capacity_litres = cleaned["tank_capacity_litres"],
                building             = cleaned["building"],
                location_note        = cleaned["location_note"],
                status               = cleaned["status"],
                installed_date       = cleaned["installed_date"],
                needs_monthly_fuel   = cleaned["needs_monthly_fuel"],
                notes                = cleaned["notes"],
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="generators",
                record_id=str(gen.pk),
                detail=f"Registered generator {gen.tag} ({gen.name})"
            )
            messages.success(request, f"Generator '{gen.tag}' registered.")
            return redirect("generators:detail", pk=gen.pk)

        return render(request, "generators/form.html", {
            "errors": errors, "post": request.POST,
            "status_choices": Generator.STATUS_CHOICES,
            "fuel_choices": Generator.FUEL_CHOICES,
        })

    return render(request, "generators/form.html", {
        "status_choices": Generator.STATUS_CHOICES,
        "fuel_choices": Generator.FUEL_CHOICES,
    })


@login_required
def edit_view(request, pk):
    if not request.user.has_module_perm("generators", "edit"):
        return HttpResponseForbidden()
    gen = get_object_or_404(Generator, pk=pk)

    if request.method == "POST":
        cleaned, errors = _validate_generator_form(request, instance=gen)

        if not errors:
            gen.tag                  = cleaned["tag"]
            gen.name                 = cleaned["name"]
            gen.make                 = cleaned["make"]
            gen.model                = cleaned["model"]
            gen.serial_number        = cleaned["serial_number"]
            gen.kva_rating           = cleaned["kva_rating"]
            gen.fuel_type            = cleaned["fuel_type"]
            gen.tank_capacity_litres = cleaned["tank_capacity_litres"]
            gen.building             = cleaned["building"]
            gen.location_note        = cleaned["location_note"]
            gen.status               = cleaned["status"]
            gen.installed_date       = cleaned["installed_date"]
            gen.needs_monthly_fuel   = cleaned["needs_monthly_fuel"]
            gen.notes                = cleaned["notes"]
            gen.save()

            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_EDIT, module="generators",
                record_id=str(gen.pk),
                detail=f"Updated generator {gen.tag}"
            )
            messages.success(request, f"Generator '{gen.tag}' updated.")
            return redirect("generators:detail", pk=gen.pk)

        return render(request, "generators/form.html", {
            "obj": gen,
            "errors": errors, "post": request.POST,
            "status_choices": Generator.STATUS_CHOICES,
            "fuel_choices": Generator.FUEL_CHOICES,
        })

    return render(request, "generators/form.html", {
        "obj": gen,
        "status_choices": Generator.STATUS_CHOICES,
        "fuel_choices": Generator.FUEL_CHOICES,
    })


@login_required
def delete_view(request, pk):
    """
    Soft-delete via decommissioning. Hard delete would orphan fuel coupons and
    maintenance records (when those modules link to generators in Gen-2/3),
    so we mark as Inactive instead.
    """
    if not request.user.has_module_perm("generators", "delete"):
        return HttpResponseForbidden()
    gen = get_object_or_404(Generator, pk=pk)

    if request.method == "POST":
        gen.decommission()
        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_DELETE, module="generators",
            record_id=str(gen.pk),
            detail=f"Decommissioned generator {gen.tag}"
        )
        messages.success(request, f"Generator '{gen.tag}' decommissioned.")
        return redirect("generators:list")

    return render(request, "generators/delete_confirm.html", {"gen": gen})
