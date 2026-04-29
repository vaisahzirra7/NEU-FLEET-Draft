from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Driver
from audit.models import AuditLog


@login_required
def list_view(request):
    if not request.user.has_module_perm("drivers", "read"):
        return HttpResponseForbidden()

    qs = Driver.objects.all()

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(full_name__icontains=q) |
            Q(staff_id__icontains=q) |
            Q(license_no__icontains=q)
        )

    status = request.GET.get("status", "")
    if status:
        qs = qs.filter(status=status)

    return render(request, "drivers/list.html", {
        "drivers": qs,
        "q": q,
        "status_filter": status,
        "can_write": request.user.has_module_perm("drivers", "write"),
    })


@login_required
def detail_view(request, pk):
    if not request.user.has_module_perm("drivers", "read"):
        return HttpResponseForbidden()

    driver  = get_object_or_404(Driver, pk=pk)
    coupons = driver.coupons.select_related("vehicle").order_by("-issue_datetime")[:15]

    return render(request, "drivers/detail.html", {
        "driver": driver,
        "coupons": coupons,
        "can_edit": request.user.has_module_perm("drivers", "edit"),
    })


@login_required
def create_view(request):
    if not request.user.has_module_perm("drivers", "write"):
        return HttpResponseForbidden()

    if request.method == "POST":
        errors = {}
        staff_id   = request.POST.get("staff_id", "").strip()
        license_no = request.POST.get("license_no", "").strip()

        if not request.POST.get("full_name"):    errors["full_name"]       = "Full name is required."
        if not staff_id:                          errors["staff_id"]        = "Staff ID is required."
        elif Driver.objects.filter(staff_id=staff_id).exists():
            errors["staff_id"] = "A driver with this Staff ID already exists."
        if not request.POST.get("phone"):         errors["phone"]           = "Phone is required."
        if not license_no:                         errors["license_no"]      = "License number is required."
        elif Driver.objects.filter(license_no=license_no).exists():
            errors["license_no"] = "A driver with this license number already exists."
        if not request.POST.get("license_class"): errors["license_class"]   = "License class is required."
        if not request.POST.get("license_expiry"):errors["license_expiry"]  = "License expiry date is required."

        if not errors:
            d = Driver.objects.create(
                full_name      = request.POST["full_name"].strip(),
                staff_id       = staff_id,
                phone          = request.POST["phone"].strip(),
                license_no     = license_no,
                license_class  = request.POST["license_class"],
                license_expiry = request.POST["license_expiry"],
                status         = request.POST.get("status", Driver.STATUS_ACTIVE),
                notes          = request.POST.get("notes", "").strip(),
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="drivers",
                record_id=str(d.pk), detail=f"Registered driver {d.full_name}"
            )
            messages.success(request, f"Driver '{d.full_name}' registered successfully.")
            return redirect("drivers:detail", pk=d.pk)

        return render(request, "drivers/form.html", {
            "errors": errors,
            "full_name_val":      request.POST.get("full_name", ""),
            "staff_id_val":       request.POST.get("staff_id", ""),
            "phone_val":          request.POST.get("phone", ""),
            "license_no_val":     request.POST.get("license_no", ""),
            "license_expiry_val": request.POST.get("license_expiry", ""),
            "license_class_val":  request.POST.get("license_class", ""),
            "status_val":         request.POST.get("status", ""),
            "notes_val":          request.POST.get("notes", ""),
            "license_classes": Driver.LICENSE_CLASSES,
            "status_choices": Driver.STATUS_CHOICES,
        })

    return render(request, "drivers/form.html", {
        "license_classes": Driver.LICENSE_CLASSES,
        "status_choices": Driver.STATUS_CHOICES,
    })


@login_required
def edit_view(request, pk):
    if not request.user.has_module_perm("drivers", "edit"):
        return HttpResponseForbidden()

    driver = get_object_or_404(Driver, pk=pk)

    if request.method == "POST":
        driver.full_name      = request.POST.get("full_name", driver.full_name).strip()
        driver.phone          = request.POST.get("phone", driver.phone).strip()
        driver.license_class  = request.POST.get("license_class", driver.license_class)
        driver.license_expiry = request.POST.get("license_expiry", driver.license_expiry)
        driver.status         = request.POST.get("status", driver.status)
        driver.notes          = request.POST.get("notes", "").strip()
        driver.save()

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_EDIT, module="drivers",
            record_id=str(driver.pk), detail=f"Updated driver {driver.full_name}"
        )
        messages.success(request, f"Driver '{driver.full_name}' updated.")
        return redirect("drivers:detail", pk=driver.pk)

    return render(request, "drivers/form.html", {
        "obj": driver,
        "license_classes": Driver.LICENSE_CLASSES,
        "status_choices": Driver.STATUS_CHOICES,
    })
