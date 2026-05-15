from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import User, Role, RoleModulePermission, Department
from audit.models import AuditLog


# ── Auth ──────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None
    if request.method == "POST":
        email    = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user:
            if not user.is_active:
                error = "Your account is inactive. Contact your administrator."
            else:
                login(request, user)
                AuditLog.objects.create(
                    user=user,
                    user_name=user.full_name,
                    action=AuditLog.ACTION_LOGIN,
                    module="accounts",
                    record_id=str(user.pk),
                    detail=f"{user.full_name} logged in.",
                )
                next_url = request.GET.get("next", "dashboard")
                return redirect(next_url)
        else:
            error = "Invalid email or password. Please try again."

    return render(request, "accounts/login.html", {
        "error": error,
        "email_value": request.POST.get("username", "") if request.method == "POST" else "",
    })


def logout_view(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                user_name=request.user.full_name,
                action=AuditLog.ACTION_LOGOUT,
                module="accounts",
                record_id=str(request.user.pk),
                detail=f"{request.user.full_name} logged out.",
            )
        logout(request)
    return redirect("accounts:login")


# ── Password Reset (OTP flow) ──────────────────────────────────

def password_reset_request(request):
    """Step 1 — user enters their email, OTP is sent."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        from .models import PasswordResetOTP
        import random, os
        from django.core.mail import EmailMultiAlternatives
        from django.core.mail import SafeMIMEMultipart
        from email.mime.image import MIMEImage
        from django.conf import settings

        email = request.POST.get("email", "").strip()
        try:
            user = User.objects.get(email=email, is_active=True)
            otp  = str(random.randint(100000, 999999))
            PasswordResetOTP.objects.create(user=user, otp=otp)

            otp_display = " ".join(otp)

            html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Password Reset OTP</title>
</head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 16px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

        <!-- Header -->
        <tr>
          <td style="background:#0f2044;border-radius:16px 16px 0 0;padding:28px 36px;text-align:center;">
            <img src="cid:neu_logo" alt="NEU Logo"
              style="width:72px;height:72px;object-fit:contain;margin-bottom:14px;display:block;margin-left:auto;margin-right:auto;">
            <div style="font-size:20px;font-weight:700;color:#ffffff;letter-spacing:-.3px;">VanaraFleetsOps</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.45);margin-top:4px;">North-Eastern University, Gombe &nbsp;&middot;&nbsp; Fleet Management System</div>
          </td>
        </tr>

        <!-- Amber accent bar -->
        <tr><td style="background:#c8813a;height:4px;"></td></tr>

        <!-- Body -->
        <tr>
          <td style="background:#ffffff;padding:40px 36px 32px;">
            <p style="margin:0 0 8px;font-size:15px;font-weight:600;color:#0f2044;">Hello, {user.full_name}</p>
            <p style="margin:0 0 28px;font-size:14px;color:#5a6480;line-height:1.7;">
              We received a request to reset the password for your VanaraFleetsOps account.
              Use the one-time code below to proceed. The code expires in <strong>15 minutes</strong>.
            </p>

            <!-- OTP Block -->
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
              <tr>
                <td align="center" style="background:#f4f6fa;border:1px solid #dde2ed;border-radius:12px;padding:28px 20px;">
                  <div style="font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#8a96b3;margin-bottom:12px;">Your Reset Code</div>
                  <div style="font-size:42px;font-weight:800;letter-spacing:.18em;color:#0f2044;font-family:'Courier New',monospace;line-height:1;">{otp_display}</div>
                  <div style="font-size:12px;color:#b0b8cc;margin-top:12px;">Valid for 15 minutes &nbsp;&middot;&nbsp; Single use only</div>
                </td>
              </tr>
            </table>

            <p style="margin:0 0 12px;font-size:13px;color:#5a6480;line-height:1.7;">
              Enter this code on the password reset page to continue. Once used, the code will no longer be valid.
            </p>
            <p style="margin:0;font-size:13px;color:#8a96b3;line-height:1.7;">
              If you did not request a password reset, you can safely ignore this email.
              Your password will remain unchanged.
            </p>
          </td>
        </tr>

        <!-- Security notice -->
        <tr>
          <td style="background:#fdf8f0;border-left:3px solid #c8813a;padding:16px 36px;">
            <p style="margin:0;font-size:12px;color:#8a6020;line-height:1.6;">
              <strong>Security reminder:</strong> VanaraFleetsOps staff will never ask for your password or OTP.
              Do not share this code with anyone.
            </p>
          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#f4f6fa;border-radius:0 0 16px 16px;padding:20px 36px;text-align:center;">
            <p style="margin:0 0 4px;font-size:11px;color:#8a96b3;">
              This email was sent by VanaraFleetsOps on behalf of<br>
              <strong style="color:#5a6480;">North-Eastern University, Gombe &nbsp;&middot;&nbsp; Fleet Management System</strong>
            </p>
            <p style="margin:8px 0 0;font-size:11px;color:#b0b8cc;">
              This is an automated message. Please do not reply to this email.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

            plain_body = (
                f"Hello {user.full_name},\n\n"
                f"Your VanaraFleetsOps password reset code is: {otp}\n\n"
                f"This code expires in 15 minutes. Do not share it with anyone.\n\n"
                f"If you did not request this, please ignore this email.\n\n"
                f"— VanaraFleetsOps, North-Eastern University, Gombe"
            )

            msg = EmailMultiAlternatives(
                subject="VanaraFleetsOps — Your Password Reset Code",
                body=plain_body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "fleet@neu.edu.ng"),
                to=[user.email],
            )
            msg.attach_alternative(html_body, "text/html")
            msg.mixed_subtype = "related"

            # Attach logo as CID inline image
            logo_path = getattr(settings, "REPORT_LOGO_PATH", None)
            if logo_path and os.path.exists(str(logo_path)):
                with open(str(logo_path), "rb") as f:
                    logo_img = MIMEImage(f.read(), _subtype="png")
                    logo_img.add_header("Content-ID", "<neu_logo>")
                    logo_img.add_header("Content-Disposition", "inline", filename="neu_logo.png")
                    msg.attach(logo_img)

            msg.send(fail_silently=True)

        except User.DoesNotExist:
            pass

        # Store email in session to carry to OTP verification step
        request.session["reset_email"] = email
        return redirect("accounts:password_reset_verify")

    return render(request, "accounts/password_reset_request.html")


def password_reset_verify(request):
    """Step 2 — user enters the 6-digit OTP."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    email = request.session.get("reset_email", "")
    if not email:
        return redirect("accounts:password_reset_request")

    error = None

    if request.method == "POST":
        from .models import PasswordResetOTP
        otp_input = request.POST.get("otp", "").strip()

        try:
            user = User.objects.get(email=email, is_active=True)
            otp_obj = (
                PasswordResetOTP.objects
                .filter(user=user, otp=otp_input, used=False)
                .order_by("-created_at")
                .first()
            )
            if otp_obj and otp_obj.is_valid():
                # Mark used and store verified flag in session
                otp_obj.used = True
                otp_obj.save(update_fields=["used"])
                request.session["reset_verified_user"] = user.pk
                return redirect("accounts:password_reset_confirm")
            else:
                error = "Invalid or expired OTP. Please try again or request a new one."
        except User.DoesNotExist:
            error = "Something went wrong. Please start over."

    return render(request, "accounts/password_reset_verify.html", {
        "error": error,
        "email": email,
    })


def password_reset_confirm(request):
    """Step 3 — user sets their new password."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    user_pk = request.session.get("reset_verified_user")
    if not user_pk:
        return redirect("accounts:password_reset_request")

    error = None

    if request.method == "POST":
        from django.contrib.auth import login as auth_login
        new_pw  = request.POST.get("new_password", "").strip()
        confirm = request.POST.get("confirm_password", "").strip()
        DEFAULT_PW = "Neu@12345"

        if not new_pw:
            error = "Please enter a new password."
        elif len(new_pw) < 8:
            error = "Password must be at least 8 characters."
        elif new_pw != confirm:
            error = "Passwords do not match."
        elif new_pw == DEFAULT_PW:
            error = "Please choose a different password — do not use the system default."

        if not error:
            try:
                user = User.objects.get(pk=user_pk)
                user.set_password(new_pw)
                user.must_change_password = False
                user.save(update_fields=["password", "must_change_password"])

                # Clean up session
                del request.session["reset_email"]
                del request.session["reset_verified_user"]

                AuditLog.objects.create(
                    user=user, user_name=user.full_name,
                    action=AuditLog.ACTION_EDIT, module="accounts",
                    record_id=str(user.pk),
                    detail=f"{user.full_name} reset their password via OTP."
                )
                messages.success(request, "Password reset successfully. Please sign in.")
                return redirect("accounts:login")
            except User.DoesNotExist:
                return redirect("accounts:password_reset_request")

    return render(request, "accounts/password_reset_confirm.html", {"error": error})

def _build_perm_rows(modules, role=None):
    """Build permission row dicts for the role form template."""
    perms_map = {}
    if role:
        perms_map = {p.module: p for p in role.permissions.all()}
    rows = []
    # Modules where the "approve" permission is meaningful (currently coupons only).
    APPROVE_MODULES = {"coupons"}
    for key, label in modules:
        p = perms_map.get(key)
        rows.append({
            "key":         key,
            "label":       label,
            "can_read":    p.can_read    if p else False,
            "can_write":   p.can_write   if p else False,
            "can_edit":    p.can_edit    if p else False,
            "can_delete":  p.can_delete  if p else False,
            "can_approve": p.can_approve if p else False,
            "supports_approve": key in APPROVE_MODULES,
        })
    return rows




# ── User Management ───────────────────────────────────────────
@login_required
def users_list(request):
    if not request.user.has_module_perm("users", "read"):
        return HttpResponseForbidden(render(request, "403.html"))

    users = User.objects.select_related("role", "department").order_by("full_name")
    return render(request, "accounts/users_list.html", {"users": users})


DEFAULT_PASSWORD = "Neu@12345"


@login_required
def user_create(request):
    if not request.user.has_module_perm("users", "write"):
        return HttpResponseForbidden()

    roles       = Role.objects.all()
    departments = Department.objects.filter(is_active=True)

    if request.method == "POST":
        full_name  = request.POST.get("full_name", "").strip()
        email      = request.POST.get("email", "").strip()
        role_id    = request.POST.get("role")
        dept_id    = request.POST.get("department")

        errors = {}
        if not full_name: errors["full_name"] = "Full name is required."
        if not email:     errors["email"]     = "Email is required."
        if not role_id:   errors["role"]      = "Please select a role."
        if User.objects.filter(email=email).exists():
            errors["email"] = "A user with this email already exists."

        if not errors:
            user = User.objects.create_user(
                email=email, full_name=full_name,
                password=DEFAULT_PASSWORD,
                role_id=role_id or None,
                department_id=dept_id or None,
                created_by=request.user,
                must_change_password=True,
            )
            messages.success(request, f"User '{user.full_name}' created. They will be prompted to change their password on first login.")
            return redirect("accounts:users")

        return render(request, "accounts/user_form.html", {
            "errors": errors, "roles": roles, "departments": departments,
            "post": request.POST,
        })

    return render(request, "accounts/user_form.html", {
        "roles": roles, "departments": departments
    })


@login_required
def user_edit(request, pk):
    if not request.user.has_module_perm("users", "edit"):
        return HttpResponseForbidden()

    user        = get_object_or_404(User, pk=pk)
    roles       = Role.objects.all()
    departments = Department.objects.filter(is_active=True)

    if request.method == "POST":
        action = request.POST.get("action", "save")

        # Password reset
        if action == "reset_password":
            user.set_password(DEFAULT_PASSWORD)
            user.must_change_password = True
            user.save(update_fields=["password", "must_change_password"])
            messages.success(request, f"Password for '{user.full_name}' has been reset to the default. They will be prompted to change it on next login.")
            return redirect("accounts:users")

        user.full_name     = request.POST.get("full_name", user.full_name).strip()
        user.role_id       = request.POST.get("role") or None
        user.department_id = request.POST.get("department") or None
        user.is_active     = request.POST.get("is_active") == "on"
        user.save()
        messages.success(request, f"User '{user.full_name}' updated.")
        return redirect("accounts:users")

    return render(request, "accounts/user_form.html", {
        "obj": user, "roles": roles, "departments": departments
    })


@login_required
def change_password(request):
    """Handles forced and voluntary password changes."""
    if request.method == "POST":
        new_pw  = request.POST.get("new_password", "").strip()
        confirm = request.POST.get("confirm_password", "").strip()
        error   = None

        if not new_pw:
            error = "Please enter a new password."
        elif len(new_pw) < 8:
            error = "Password must be at least 8 characters."
        elif new_pw != confirm:
            error = "Passwords do not match."
        elif new_pw == DEFAULT_PASSWORD:
            error = "Please choose a different password — do not use the default."

        if error:
            return render(request, "accounts/change_password.html", {"error": error, "forced": request.user.must_change_password})

        request.user.set_password(new_pw)
        request.user.must_change_password = False
        request.user.save(update_fields=["password", "must_change_password"])
        # Re-authenticate so session stays valid after password change
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)
        messages.success(request, "Password changed successfully.")
        return redirect("dashboard")

    return render(request, "accounts/change_password.html", {"forced": request.user.must_change_password})


# ── Role Management ───────────────────────────────────────────
@login_required
def roles_list(request):
    if not request.user.has_module_perm("roles", "read"):
        return HttpResponseForbidden()
    roles = Role.objects.prefetch_related("permissions").all()
    return render(request, "accounts/roles_list.html", {"roles": roles})


@login_required
def role_create(request):
    if not request.user.has_module_perm("roles", "write"):
        return HttpResponseForbidden()

    modules = RoleModulePermission.MODULE_CHOICES

    if request.method == "POST":
        name        = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Role name is required.")
            perm_rows = _build_perm_rows(modules)
            return render(request, "accounts/role_form.html", {"modules": modules, "perm_rows": perm_rows, "post": request.POST})

        role = Role.objects.create(name=name, description=description)

        # Save permissions for each module
        for module_key, _ in modules:
            can_read    = f"perm_{module_key}_read"    in request.POST
            can_write   = f"perm_{module_key}_write"   in request.POST
            can_edit    = f"perm_{module_key}_edit"    in request.POST
            can_delete  = f"perm_{module_key}_delete"  in request.POST
            can_approve = f"perm_{module_key}_approve" in request.POST
            if can_read or can_write or can_edit or can_delete or can_approve:
                RoleModulePermission.objects.create(
                    role=role, module=module_key,
                    can_read=can_read, can_write=can_write,
                    can_edit=can_edit, can_delete=can_delete,
                    can_approve=can_approve,
                )

        messages.success(request, f"Role '{role.name}' created.")
        return redirect("accounts:roles")

    perm_rows = _build_perm_rows(modules)
    return render(request, "accounts/role_form.html", {"modules": modules, "perm_rows": perm_rows})


@login_required
def role_edit(request, pk):
    if not request.user.has_module_perm("roles", "edit"):
        return HttpResponseForbidden()

    role    = get_object_or_404(Role, pk=pk)
    modules = RoleModulePermission.MODULE_CHOICES
    perms   = {p.module: p for p in role.permissions.all()}

    if request.method == "POST":
        if role.is_system_role:
            messages.error(request, "System roles cannot be modified.")
            return redirect("accounts:roles")

        role.name        = request.POST.get("name", role.name).strip()
        role.description = request.POST.get("description", "").strip()
        role.save()

        # Rebuild permissions
        role.permissions.all().delete()
        for module_key, _ in modules:
            can_read    = f"perm_{module_key}_read"    in request.POST
            can_write   = f"perm_{module_key}_write"   in request.POST
            can_edit    = f"perm_{module_key}_edit"    in request.POST
            can_delete  = f"perm_{module_key}_delete"  in request.POST
            can_approve = f"perm_{module_key}_approve" in request.POST
            if can_read or can_write or can_edit or can_delete or can_approve:
                RoleModulePermission.objects.create(
                    role=role, module=module_key,
                    can_read=can_read, can_write=can_write,
                    can_edit=can_edit, can_delete=can_delete,
                    can_approve=can_approve,
                )

        messages.success(request, f"Role '{role.name}' updated.")
        return redirect("accounts:roles")

    perm_rows = _build_perm_rows(modules, role)
    return render(request, "accounts/role_form.html", {
        "obj": role, "modules": modules, "perm_rows": perm_rows
    })


# ── Department Management ─────────────────────────────────────
@login_required
def departments_list(request):
    if not request.user.is_system_admin:
        return HttpResponseForbidden()

    departments = Department.objects.all().order_by("name")
    return render(request, "accounts/departments_list.html", {
        "departments": departments
    })


@login_required
def department_create(request):
    if not request.user.is_system_admin:
        return HttpResponseForbidden()

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip().upper()
        errors = {}

        if not name: errors["name"] = "Department name is required."
        if not code: errors["code"] = "Department code is required."
        if Department.objects.filter(name__iexact=name).exists():
            errors["name"] = "A department with this name already exists."
        if Department.objects.filter(code__iexact=code).exists():
            errors["code"] = "This code is already in use."

        if not errors:
            dept = Department.objects.create(name=name, code=code)
            messages.success(request, f"Department '{dept.name}' created.")
            return redirect("accounts:departments")

        return render(request, "accounts/department_form.html", {
            "errors": errors,
            "name_value": request.POST.get("name", ""),
            "code_value": request.POST.get("code", ""),
        })

    return render(request, "accounts/department_form.html", {})


@login_required
def department_edit(request, pk):
    if not request.user.is_system_admin:
        return HttpResponseForbidden()

    dept = get_object_or_404(Department, pk=pk)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "toggle_active":
            dept.is_active = not dept.is_active
            dept.save(update_fields=["is_active"])
            state = "activated" if dept.is_active else "deactivated"
            messages.success(request, f"Department '{dept.name}' {state}.")
            return redirect("accounts:departments")

        dept.name = request.POST.get("name", dept.name).strip()
        dept.code = request.POST.get("code", dept.code).strip().upper()
        dept.save()
        messages.success(request, f"Department '{dept.name}' updated.")
        return redirect("accounts:departments")

    return render(request, "accounts/department_form.html", {"obj": dept})


# ── Profile ──────────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    user = request.user
    error = None
    pw_error = None
    pw_success = False

    if request.method == "POST":
        action = request.POST.get("action", "profile")

        if action == "profile":
            full_name = request.POST.get("full_name", "").strip()
            phone     = request.POST.get("phone", "").strip()
            if not full_name:
                error = "Full name cannot be empty."
            else:
                user.full_name = full_name
                if hasattr(user, "phone"):
                    user.phone = phone
                user.save(update_fields=["full_name"] + (["phone"] if hasattr(user, "phone") else []))
                from audit.models import AuditLog
                AuditLog.objects.create(
                    user=user, user_name=user.full_name,
                    action=AuditLog.ACTION_EDIT, module="accounts",
                    record_id=str(user.pk),
                    detail="Updated own profile"
                )
                messages.success(request, "Profile updated successfully.")
                return redirect("accounts:profile")

        elif action == "change_password":
            current  = request.POST.get("current_password", "")
            new_pw   = request.POST.get("new_password", "").strip()
            confirm  = request.POST.get("confirm_password", "").strip()

            if not user.check_password(current):
                pw_error = "Current password is incorrect."
            elif not new_pw:
                pw_error = "New password cannot be empty."
            elif len(new_pw) < 8:
                pw_error = "Password must be at least 8 characters."
            elif new_pw != confirm:
                pw_error = "Passwords do not match."
            elif new_pw == DEFAULT_PASSWORD:
                pw_error = "Please choose a different password — do not use the system default."
            else:
                user.set_password(new_pw)
                user.must_change_password = False
                user.save(update_fields=["password", "must_change_password"])
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, "Password changed successfully.")
                return redirect("accounts:profile")

    return render(request, "accounts/profile.html", {
        "user": user,
        "error": error,
        "pw_error": pw_error,
    })
