from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import SystemSettings
from .mail import test_smtp_config
from audit.models import AuditLog


MAX_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB
ALLOWED_LOGO_EXTS    = {"png", "jpg", "jpeg", "svg", "webp", "gif"}
ALLOWED_FAVICON_EXTS = {"png", "ico", "svg"}

# Password-field sentinel: when the form is rendered, the password input shows
# this string instead of the actual encrypted value. On save we only update
# the password if the user typed something OTHER than this sentinel.
PASSWORD_SENTINEL = "********"


def _ext(name):
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""


def _can_view_branding(user):    return user.has_module_perm("settings", "read")
def _can_edit_branding(user):    return user.has_module_perm("settings", "edit")
def _can_view_smtp(user):        return user.has_module_perm("settings_email", "read")
def _can_edit_smtp(user):        return user.has_module_perm("settings_email", "edit")


@login_required
def edit_view(request):
    """
    System Settings page.

    Routes by POST 'action' field:
      - 'save_branding' - name, subtitle, logo, favicon, email_from
      - 'save_smtp'     - host/port/user/password/tls/ssl
      - 'test_smtp'     - fires a test email using currently-typed values

    Permissions:
      - settings:read       - view branding section
      - settings:edit       - save branding
      - settings_email:read - view SMTP section (password always hidden)
      - settings_email:edit - save SMTP, send test
    """
    if not (_can_view_branding(request.user) or _can_view_smtp(request.user)):
        return HttpResponseForbidden()

    obj = SystemSettings.get()
    can_edit_branding = _can_edit_branding(request.user)
    can_view_smtp     = _can_view_smtp(request.user)
    can_edit_smtp     = _can_edit_smtp(request.user)

    # Detect from-address vs SMTP-user domain mismatch
    cfg = obj.smtp_config()
    smtp_user_addr = cfg.get("username") or ""
    domain_mismatch = False
    if obj.email_from and smtp_user_addr and "@" in obj.email_from and "@" in smtp_user_addr:
        if obj.email_from.split("@", 1)[-1].lower() != smtp_user_addr.split("@", 1)[-1].lower():
            domain_mismatch = True

    if request.method == "POST":
        action = request.POST.get("action", "save_branding")

        if action == "save_branding":
            if not can_edit_branding:
                return HttpResponseForbidden()
            return _save_branding(request, obj)

        if action == "save_smtp":
            if not can_edit_smtp:
                return HttpResponseForbidden()
            return _save_smtp(request, obj)

        if action == "test_smtp":
            if not can_edit_smtp:
                return HttpResponseForbidden()
            return _test_smtp(request, obj)

        messages.error(request, "Unknown action.")
        return redirect("system_settings:edit")

    return render(request, "system_settings/edit.html", {
        "obj": obj,
        "post": {},
        "can_edit_branding": can_edit_branding,
        "can_view_smtp":     can_view_smtp,
        "can_edit_smtp":     can_edit_smtp,
        "password_sentinel": PASSWORD_SENTINEL,
        "domain_mismatch":   domain_mismatch,
        "smtp_user_addr":    smtp_user_addr,
    })


def _save_branding(request, obj):
    errors = {}
    system_name          = request.POST.get("system_name", "").strip()
    institution_name     = request.POST.get("institution_name", "").strip()
    institution_subtitle = request.POST.get("institution_subtitle", "").strip()

    if not institution_name:
        errors["institution_name"] = "Institution name is required."
    if not system_name:
        errors["system_name"] = "System name is required."

    logo_file    = request.FILES.get("logo")
    favicon_file = request.FILES.get("favicon")

    if logo_file:
        if logo_file.size > MAX_UPLOAD_BYTES:
            errors["logo"] = "Logo too large. Keep under 2 MB."
        elif _ext(logo_file.name) not in ALLOWED_LOGO_EXTS:
            errors["logo"] = "Logo must be PNG, JPG, SVG, WEBP, or GIF."

    if favicon_file:
        if favicon_file.size > MAX_UPLOAD_BYTES:
            errors["favicon"] = "Favicon too large. Keep under 2 MB."
        elif _ext(favicon_file.name) not in ALLOWED_FAVICON_EXTS:
            errors["favicon"] = "Favicon must be PNG, ICO, or SVG."

    changed_fields = []
    if not errors:
        for fld, new in [
            ("system_name", system_name),
            ("institution_name", institution_name),
            ("institution_subtitle", institution_subtitle),
        ]:
            if getattr(obj, fld) != new:
                changed_fields.append(fld)
                setattr(obj, fld, new)

        if request.POST.get("remove_logo") == "1" and obj.logo:
            obj.logo.delete(save=False)
            changed_fields.append("logo (removed)")
        if request.POST.get("remove_favicon") == "1" and obj.favicon:
            obj.favicon.delete(save=False)
            changed_fields.append("favicon (removed)")

        if logo_file:
            if obj.logo:
                obj.logo.delete(save=False)
            obj.logo = logo_file
            changed_fields.append("logo")
        if favicon_file:
            if obj.favicon:
                obj.favicon.delete(save=False)
            obj.favicon = favicon_file
            changed_fields.append("favicon")

        obj.updated_by = request.user
        obj.save()

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_EDIT, module="settings",
            record_id="1",
            detail=(
                "Updated branding: " + ", ".join(changed_fields)
                if changed_fields else "Saved branding (no changes)"
            ),
        )
        messages.success(request, "Branding settings updated.")
        return redirect("system_settings:edit")

    return render(request, "system_settings/edit.html", {
        "obj": obj, "errors": errors, "post": request.POST,
        "can_edit_branding": _can_edit_branding(request.user),
        "can_view_smtp":     _can_view_smtp(request.user),
        "can_edit_smtp":     _can_edit_smtp(request.user),
        "password_sentinel": PASSWORD_SENTINEL,
        "active_tab":        "branding",
    })


def _save_smtp(request, obj):
    errors = {}
    email_from = request.POST.get("email_from", "").strip()
    host = request.POST.get("smtp_host", "").strip()
    port = request.POST.get("smtp_port", "").strip()
    user = request.POST.get("smtp_user", "").strip()
    password = request.POST.get("smtp_password", "")
    use_tls = request.POST.get("smtp_use_tls") == "1"
    use_ssl = request.POST.get("smtp_use_ssl") == "1"

    if not email_from:
        errors["email_from"] = "From-address is required for outbound emails."
    elif "@" not in email_from:
        errors["email_from"] = "Enter a valid email address."

    any_set  = any([host, port, user])
    all_set  = all([host, port, user])
    if any_set and not all_set:
        errors["smtp_host"] = "If overriding SMTP, host, port, and username are all required."

    if port:
        try:
            port_int = int(port)
            if not (1 <= port_int <= 65535):
                raise ValueError()
        except ValueError:
            errors["smtp_port"] = "Port must be a number between 1 and 65535."

    if use_tls and use_ssl:
        errors["smtp_use_tls"] = "TLS and SSL are mutually exclusive - pick one."

    changed_fields = []
    if not errors:
        if obj.email_from != email_from:
            changed_fields.append("email_from")
            obj.email_from = email_from
        if obj.smtp_host != host:        changed_fields.append("smtp_host");  obj.smtp_host = host
        if str(obj.smtp_port or "") != port:
            changed_fields.append("smtp_port")
            obj.smtp_port = int(port) if port else None
        if obj.smtp_user != user:        changed_fields.append("smtp_user"); obj.smtp_user = user
        if obj.smtp_use_tls != use_tls:  changed_fields.append("smtp_use_tls"); obj.smtp_use_tls = use_tls
        if obj.smtp_use_ssl != use_ssl:  changed_fields.append("smtp_use_ssl"); obj.smtp_use_ssl = use_ssl

        if password != PASSWORD_SENTINEL:
            if password == "":
                if obj.smtp_password_encrypted:
                    changed_fields.append("smtp_password (cleared)")
                obj.set_smtp_password("")
            else:
                changed_fields.append("smtp_password (updated)")
                obj.set_smtp_password(password)

        obj.updated_by = request.user
        obj.save()

        AuditLog.objects.create(
            user=request.user, user_name=request.user.full_name,
            action=AuditLog.ACTION_EDIT, module="settings_email",
            record_id="1",
            detail=(
                "Updated SMTP config: " + ", ".join(changed_fields)
                if changed_fields else "Saved SMTP config (no changes)"
            ),
        )
        messages.success(request, "SMTP settings updated.")
        return redirect("system_settings:edit")

    return render(request, "system_settings/edit.html", {
        "obj": obj, "errors": errors, "post": request.POST,
        "can_edit_branding": _can_edit_branding(request.user),
        "can_view_smtp":     _can_view_smtp(request.user),
        "can_edit_smtp":     _can_edit_smtp(request.user),
        "password_sentinel": PASSWORD_SENTINEL,
        "active_tab":        "smtp",
    })


def _test_smtp(request, obj):
    """
    Send a test email using currently-typed (or saved) SMTP values.

    Order of resolution per field:
      1. Value posted by the form (lets admin test BEFORE saving)
      2. Fall back to the saved DB / settings.py via smtp_config()
    """
    from django.conf import settings as dsettings
    cfg = obj.smtp_config()

    host = request.POST.get("smtp_host", "").strip()    or cfg["host"]
    port = request.POST.get("smtp_port", "").strip()    or cfg["port"]
    user = request.POST.get("smtp_user", "").strip()    or cfg["username"]
    password_input = request.POST.get("smtp_password", "")
    if password_input and password_input != PASSWORD_SENTINEL:
        password = password_input
    else:
        password = cfg["password"]

    # Boolean form-vs-saved resolution: presence of any SMTP form input
    # signals "use form values"; otherwise use saved.
    if any(request.POST.get(k) for k in ("smtp_host", "smtp_port", "smtp_user")):
        use_tls = request.POST.get("smtp_use_tls") == "1"
        use_ssl = request.POST.get("smtp_use_ssl") == "1"
    else:
        use_tls = cfg["use_tls"]
        use_ssl = cfg["use_ssl"]

    from_addr = (request.POST.get("email_from") or obj.email_from or "noreply@example.com").strip()
    to_addr   = (request.POST.get("test_recipient") or request.user.email or "").strip()

    if not to_addr:
        messages.error(request, "Cannot send test - your account has no email address.")
        return redirect("system_settings:edit")

    if not host or not port or not user:
        messages.error(request, "Cannot send test - fill host, port, and username first.")
        return redirect("system_settings:edit")

    ok, err = test_smtp_config(
        host=host, port=port, username=user, password=password,
        use_tls=use_tls, use_ssl=use_ssl,
        from_addr=from_addr, to_addr=to_addr,
    )

    AuditLog.objects.create(
        user=request.user, user_name=request.user.full_name,
        action=AuditLog.ACTION_EDIT, module="settings_email",
        record_id="1",
        detail=f"SMTP test send to {to_addr} - {'OK' if ok else f'failed: {err}'}",
    )

    if ok:
        messages.success(request, f"Test email sent to {to_addr}. Check your inbox.")
    else:
        detail = f" Details: {err}" if dsettings.DEBUG else ""
        messages.error(
            request,
            f"Test email FAILED.{detail} Check SMTP credentials and from-address."
        )
    return redirect("system_settings:edit")
