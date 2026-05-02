from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from .models import AuditLog


@login_required
def list_view(request):
    if not request.user.has_module_perm("audit", "read"):
        return HttpResponseForbidden()

    qs = AuditLog.objects.select_related("user").all()

    # Filters
    action   = request.GET.get("action", "").strip()
    module   = request.GET.get("module", "").strip()
    user_q   = request.GET.get("user", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    date_to   = request.GET.get("date_to", "").strip()

    if action:
        qs = qs.filter(action=action)
    if module:
        qs = qs.filter(module=module)
    if user_q:
        qs = qs.filter(user_name__icontains=user_q)
    if date_from:
        qs = qs.filter(timestamp__date__gte=date_from)
    if date_to:
        qs = qs.filter(timestamp__date__lte=date_to)

    # Distinct modules for filter dropdown
    modules = AuditLog.objects.values_list("module", flat=True).distinct().order_by("module")

    paginator = Paginator(qs, 50)
    page      = paginator.get_page(request.GET.get("page"))

    return render(request, "audit/list.html", {
        "page":           page,
        "logs":           page.object_list,
        "action_choices": AuditLog.ACTION_CHOICES,
        "modules":        modules,
        "filters": {
            "action":    action,
            "module":    module,
            "user":      user_q,
            "date_from": date_from,
            "date_to":   date_to,
        },
        "total": paginator.count,
    })
