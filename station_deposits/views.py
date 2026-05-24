from decimal import Decimal, InvalidOperation
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q

from vendors.models import Vendor
from audit.models import AuditLog
from .models import StationDeposit


@login_required
def list_view(request):
    """All deposits across all stations, with filters."""
    if not request.user.has_module_perm("station_deposits", "read"):
        return HttpResponseForbidden()

    qs = StationDeposit.objects.select_related("vendor", "created_by").all()

    # Filters
    station_id = request.GET.get("station", "").strip()
    date_from  = request.GET.get("date_from", "").strip()
    date_to    = request.GET.get("date_to", "").strip()
    q_search   = request.GET.get("q", "").strip()

    if station_id:
        qs = qs.filter(vendor_id=station_id)
    if date_from:
        qs = qs.filter(deposit_date__gte=date_from)
    if date_to:
        qs = qs.filter(deposit_date__lte=date_to)
    if q_search:
        qs = qs.filter(
            Q(reference_number__icontains=q_search) |
            Q(note__icontains=q_search) |
            Q(created_by__full_name__icontains=q_search)
        )

    stations = Vendor.objects.filter(type=Vendor.TYPE_FUEL, is_active=True).order_by("name")
    return render(request, "station_deposits/list.html", {
        "deposits": qs,
        "stations": stations,
        "filter_station_id": station_id,
        "filter_date_from":  date_from,
        "filter_date_to":    date_to,
        "filter_q":          q_search,
        "can_write":         request.user.has_module_perm("station_deposits", "write"),
        "can_delete":        request.user.has_module_perm("station_deposits", "delete"),
    })


@login_required
def create_view(request):
    """Record a new deposit. Deposits are immutable once created."""
    if not request.user.has_module_perm("station_deposits", "write"):
        return HttpResponseForbidden()

    stations = Vendor.objects.filter(type=Vendor.TYPE_FUEL, is_active=True).order_by("name")
    errors = {}
    post   = request.POST if request.method == "POST" else {}

    # Pre-select a station if ?station=<id> in URL (e.g. from vendor detail page)
    preselect = request.GET.get("station", "")

    if request.method == "POST":
        vendor_id    = request.POST.get("vendor", "").strip()
        amount_raw   = request.POST.get("amount", "").strip()
        deposit_date = request.POST.get("deposit_date", "").strip()
        reference    = request.POST.get("reference_number", "").strip()
        note         = request.POST.get("note", "").strip()

        # Validate station
        try:
            vendor = Vendor.objects.get(pk=vendor_id, type=Vendor.TYPE_FUEL, is_active=True)
        except (Vendor.DoesNotExist, ValueError):
            errors["vendor"] = "Choose a valid active fuel station."
            vendor = None

        # Validate amount
        amount = None
        if not amount_raw:
            errors["amount"] = "Amount is required."
        else:
            try:
                amount = Decimal(amount_raw.replace(",", ""))
                if amount <= 0:
                    errors["amount"] = "Amount must be greater than zero."
            except (InvalidOperation, ValueError):
                errors["amount"] = "Enter a valid number."

        # Validate date
        if not deposit_date:
            errors["deposit_date"] = "Deposit date is required."

        if not errors:
            deposit = StationDeposit.objects.create(
                vendor=vendor,
                amount=amount,
                deposit_date=deposit_date,
                reference_number=reference,
                note=note,
                created_by=request.user,
            )
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="station_deposits",
                record_id=str(deposit.pk),
                detail=f"Recorded deposit of \u20a6{amount:,.2f} to {vendor.name} dated {deposit_date}"
                       + (f" (ref: {reference})" if reference else ""),
            )
            messages.success(request,
                f"Deposit of \u20a6{amount:,.2f} recorded for {vendor.name}. "
                f"New balance: \u20a6{vendor.balance:,.2f}"
            )
            return redirect("vendors:detail", pk=vendor.pk)

    return render(request, "station_deposits/form.html", {
        "stations":     stations,
        "errors":       errors,
        "post":         post,
        "preselect":    preselect,
        "today":        date.today().isoformat(),
    })


@login_required
def delete_view(request, pk):
    """
    Delete an erroneous deposit. Super-admin-only per the policy decision.

    Per Q5 of the planning round: deposits cannot be edited; the only
    correction mechanism is deletion by a Super Admin. The audit log
    captures the original amount and station so the trail is intact
    even after the row is gone.
    """
    deposit = get_object_or_404(StationDeposit, pk=pk)

    # Tighter check than the standard "delete" perm: only system admins
    # can actually pull the trigger on deletion, even if a role has
    # station_deposits:delete granted.
    if not request.user.is_system_admin:
        return HttpResponseForbidden(
            "Only a Super Admin can delete a deposit. "
            "If this deposit is wrong, contact a Super Admin."
        )

    if request.method == "POST":
        # Capture details BEFORE delete so the audit log keeps them
        snapshot = (
            f"Deleted deposit #{deposit.pk}: \u20a6{deposit.amount:,.2f} to "
            f"{deposit.vendor.name} dated {deposit.deposit_date}"
            + (f" (ref: {deposit.reference_number})" if deposit.reference_number else "")
            + f". Original recorder: {deposit.created_by.full_name}."
        )
        vendor_pk = deposit.vendor_id
        deposit.delete()

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_DELETE, module="station_deposits",
            record_id=str(pk),
            detail=snapshot,
        )
        messages.success(request, "Deposit deleted.")
        return redirect("vendors:detail", pk=vendor_pk)

    return render(request, "station_deposits/delete_confirm.html", {"deposit": deposit})
