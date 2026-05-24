from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import User, Role, RoleModulePermission, Department, UserInvite
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

            from system_settings.mail import get_mail_connection
            msg = EmailMultiAlternatives(
                subject="VanaraFleetsOps — Your Password Reset Code",
                body=plain_body,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "fleet@neu.edu.ng"),
                to=[user.email],
                connection=get_mail_connection(),
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
    """
    Build permission row dicts for the role form template.

    Each module declares which of read/write/edit/delete/approve are
    meaningful for it. Permissions that don't apply are rendered as "—"
    in the grid instead of as a checkbox — so admins can't tick a box
    that the view layer will never check.

    Adding a new permission to a module = update MODULE_CAPABILITIES below
    AND update the view that should enforce it.
    """
    perms_map = {p.module: p for p in role.permissions.all()} if role else {}

    # Per-module capability matrix.
    # Keep this in sync with what the views actually enforce — entries here
    # that no view checks are dead UI; entries the views check that aren't
    # here mean the admin can't grant the permission.
    DEFAULT_CAPS = {"read", "write", "edit", "delete"}
    MODULE_CAPABILITIES = {
        "vehicles":       {"read", "write", "edit", "delete"},
        "generators":     {"read", "write", "edit", "delete"},
        "drivers":        {"read", "write", "edit", "delete"},
        "coupons":        {"read", "write", "edit", "delete", "approve"},
        "fuel_logs":      {"read", "write"},
        "maintenance":    {"read", "write", "edit"},
        "vendors":        {"read", "write", "edit", "delete"},
        "reports":        {"read"},
        "dashboard":      {"read"},
        "users":          {"read", "write", "edit"},
        "roles":          {"read", "write", "edit", "delete"},
        "audit":          {"read"},
        "trips":          {"read", "write", "edit"},
        "destinations":   {"read", "write", "edit"},
        "settings":       {"read", "edit"},
        "settings_email": {"read", "edit"},
        "station_deposits": {"read", "write", "delete"},
    }

    rows = []
    for key, label in modules:
        p = perms_map.get(key)
        caps = MODULE_CAPABILITIES.get(key, DEFAULT_CAPS)
        rows.append({
            "key":            key,
            "label":          label,
            "can_read":       p.can_read    if p else False,
            "can_write":      p.can_write   if p else False,
            "can_edit":       p.can_edit    if p else False,
            "can_delete":     p.can_delete  if p else False,
            "can_approve":    p.can_approve if p else False,
            "supports_read":     "read"    in caps,
            "supports_write":    "write"   in caps,
            "supports_edit":     "edit"    in caps,
            "supports_delete":   "delete"  in caps,
            "supports_approve":  "approve" in caps,
        })
    return rows




# ── User Management ───────────────────────────────────────────
@login_required
def users_list(request):
    if not request.user.has_module_perm("users", "read"):
        return HttpResponseForbidden(render(request, "403.html"))

    users = User.objects.select_related("role", "department").order_by("full_name")
    return render(request, "accounts/users_list.html", {"users": users})


DEFAULT_PASSWORD = "Neu@12345"  # legacy — kept for backward-compat with old admin reset_password action; new flow uses invites


def _send_invite_email(invite, request):
    """
    Send the magic-link invite email to invite.user.

    Branding (logo, institution name, system name, from-address) is pulled from
    SystemSettings if available, falling back to defaults. Errors are swallowed
    so a transient SMTP issue doesn't crash user creation — the admin still
    gets the success message and can hit "Resend Invite" later.

    Returns True if the email was sent, False if it failed (so the caller can
    show a more useful message). Does NOT return on success — caller checks
    return value.
    """
    import os
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives
    from email.mime.image import MIMEImage

    # Resolve brand context
    try:
        from system_settings.models import SystemSettings
        s = SystemSettings.get()
        system_name      = s.system_name or "VanaraFleetsOps"
        institution_name = s.institution_name or "Fleet Management"
        from_email       = s.email_from or getattr(settings, "DEFAULT_FROM_EMAIL", "fleet@neu.edu.ng")
    except Exception:
        system_name      = "VanaraFleetsOps"
        institution_name = "Fleet Management"
        from_email       = getattr(settings, "DEFAULT_FROM_EMAIL", "fleet@neu.edu.ng")

    # Build the activation URL
    activation_url = request.build_absolute_uri(
        f"/auth/invite/{invite.token}/"
    )
    expires_str = invite.expires_at.strftime("%d %b %Y, %H:%M")

    plain_body = (
        f"Hello {invite.user.full_name},\n\n"
        f"An account has been created for you on {system_name}.\n\n"
        f"To set your password and start using the system, click the link below:\n"
        f"{activation_url}\n\n"
        f"This link expires on {expires_str} (24 hours from now).\n\n"
        f"If the link expires before you use it, ask your administrator to resend the invitation.\n\n"
        f"— {institution_name}"
    )

    html_body = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Welcome to {system_name}</title></head>
<body style="margin:0;padding:0;background:#f0f2f7;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f2f7;padding:40px 16px;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
        <tr>
          <td style="background:#0f2044;border-radius:16px 16px 0 0;padding:28px 36px;text-align:center;">
            <img src="cid:neu_logo" alt="Logo"
              style="width:72px;height:72px;object-fit:contain;margin-bottom:14px;display:block;margin-left:auto;margin-right:auto;">
            <div style="font-size:20px;font-weight:700;color:#ffffff;letter-spacing:-.3px;">{system_name}</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.45);margin-top:4px;">{institution_name}</div>
          </td>
        </tr>
        <tr>
          <td style="background:#ffffff;padding:36px 36px 24px;">
            <p style="margin:0 0 16px;font-size:16px;color:#0f2044;">Hello {invite.user.full_name},</p>
            <p style="margin:0 0 16px;font-size:14px;color:#5a6480;line-height:1.7;">
              An account has been created for you on <strong>{system_name}</strong>. To get started, click the button below to set your password.
            </p>
            <p style="text-align:center;margin:28px 0;">
              <a href="{activation_url}" style="background:#0f2044;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-weight:600;font-size:14px;display:inline-block;">Set Your Password</a>
            </p>
            <p style="margin:0 0 8px;font-size:12px;color:#8a96b3;">Or copy and paste this link into your browser:</p>
            <p style="margin:0 0 18px;font-size:12px;color:#0d6a9e;word-break:break-all;">{activation_url}</p>
            <p style="margin:18px 0 0;font-size:12px;color:#8a96b3;line-height:1.6;">
              This link expires on <strong>{expires_str}</strong> (24 hours from now). If it expires before you use it, ask your administrator to resend the invitation.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:#f4f6fa;border-radius:0 0 16px 16px;padding:18px 36px;text-align:center;font-size:11px;color:#8a96b3;">
            This is an automated message from {system_name}. Do not reply to this email.
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body></html>"""

    try:
        from system_settings.mail import get_mail_connection
        msg = EmailMultiAlternatives(
            subject=f"{system_name} — Welcome! Set your password",
            body=plain_body,
            from_email=from_email,
            to=[invite.user.email],
            connection=get_mail_connection(),
        )
        msg.attach_alternative(html_body, "text/html")
        msg.mixed_subtype = "related"

        # Attach institution logo as CID. Prefer SystemSettings.logo file on disk;
        # fall back to the bundled REPORT_LOGO_PATH if no custom logo uploaded.
        logo_disk_path = None
        try:
            if s.logo and s.logo.path and os.path.exists(s.logo.path):
                logo_disk_path = s.logo.path
        except Exception:
            logo_disk_path = None
        if not logo_disk_path:
            fallback = getattr(settings, "REPORT_LOGO_PATH", None)
            if fallback and os.path.exists(str(fallback)):
                logo_disk_path = str(fallback)

        if logo_disk_path:
            with open(logo_disk_path, "rb") as f:
                logo_img = MIMEImage(f.read())
                logo_img.add_header("Content-ID", "<neu_logo>")
                logo_img.add_header("Content-Disposition", "inline", filename="logo.png")
                msg.attach(logo_img)

        msg.send(fail_silently=False)
        return True, None
    except Exception as e:
        # SMTP failure, bad credentials, rejected from-address, etc.
        # Surface the real error to the runserver console AND return it so the
        # admin sees the actual cause in the toast (in DEBUG) instead of just
        # "SMTP error".
        import logging, traceback, sys
        err_text = f"{type(e).__name__}: {e}"
        print(f"\n[INVITE EMAIL FAILED] to={invite.user.email}", file=sys.stderr)
        print(f"  from={from_email}", file=sys.stderr)
        print(f"  error={err_text}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        logging.getLogger(__name__).warning(
            "Failed to send invite email to %s: %s", invite.user.email, err_text
        )
        return False, err_text


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
            # Create the user with NO usable password — they set it via invite.
            user = User.objects.create_user(
                email=email, full_name=full_name,
                password=None,  # explicit, even though create_user handles it
                role_id=role_id or None,
                department_id=dept_id or None,
                created_by=request.user,
                must_change_password=False,  # invite flow handles this differently
            )
            user.set_unusable_password()
            user.save(update_fields=["password"])

            invite = UserInvite.issue(user=user, created_by=request.user)
            ok, err = _send_invite_email(invite, request)

            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_CREATE, module="users",
                record_id=str(user.pk),
                detail=f"Created user '{user.full_name}' ({user.email}) and "
                       f"{'sent' if ok else f'attempted to send invite email (failed: {err})'}",
            )

            if ok:
                messages.success(
                    request,
                    f"User '{user.full_name}' created. An invitation email has been sent "
                    f"to {user.email} — they have 24 hours to set their password."
                )
            else:
                from django.conf import settings as _s
                detail = f" Details: {err}" if (_s.DEBUG and err) else ""
                messages.warning(
                    request,
                    f"User '{user.full_name}' was created, but the invitation email "
                    f"could not be sent.{detail} Use 'Resend Invite' on the user's "
                    f"profile to try again."
                )
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

        # Resend invite — primary mechanism for re-onboarding a user.
        # Used when the original invite expired, the email never arrived, or
        # the user lost the link. Generates a fresh 24-hour token AND clears
        # the existing password so the user must go through the invite flow.
        if action == "resend_invite":
            user.set_unusable_password()
            user.must_change_password = False
            user.save(update_fields=["password", "must_change_password"])
            invite = UserInvite.issue(user=user, created_by=request.user)
            ok, err = _send_invite_email(invite, request)
            AuditLog.objects.create(
                user=request.user, user_name=request.user.full_name,
                action=AuditLog.ACTION_EDIT, module="users",
                record_id=str(user.pk),
                detail=f"Resent invite to '{user.full_name}' ({user.email}) — "
                       f"email {'sent' if ok else f'failed: {err}'}.",
            )
            if ok:
                messages.success(
                    request,
                    f"Invitation resent to {user.email}. They have 24 hours to set their password."
                )
            else:
                from django.conf import settings as _s
                detail = f" Details: {err}" if (_s.DEBUG and err) else ""
                messages.error(
                    request,
                    f"Invitation could NOT be sent to {user.email}.{detail} "
                    f"Check the runserver console for the full traceback."
                )
            return redirect("accounts:users")

        # Legacy: hard-set the default password. Kept as an emergency escape
        # hatch if SMTP is broken — admin can hand the password to the user
        # in person. New deployments should prefer 'resend_invite'.
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

        # Save permissions for each module.
        # We re-compute the capability matrix here so that POSTing a
        # perm_dashboard_delete=on (e.g. via curl) doesn't sneak through —
        # only capabilities the module actually supports are persisted.
        cap_rows = _build_perm_rows(modules)
        cap_map = {r["key"]: r for r in cap_rows}
        for module_key, _ in modules:
            caps = cap_map.get(module_key, {})
            can_read    = caps.get("supports_read")    and f"perm_{module_key}_read"    in request.POST
            can_write   = caps.get("supports_write")   and f"perm_{module_key}_write"   in request.POST
            can_edit    = caps.get("supports_edit")    and f"perm_{module_key}_edit"    in request.POST
            can_delete  = caps.get("supports_delete")  and f"perm_{module_key}_delete"  in request.POST
            can_approve = caps.get("supports_approve") and f"perm_{module_key}_approve" in request.POST
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

        # Rebuild permissions — same capability-matrix filter as role_create
        role.permissions.all().delete()
        cap_rows = _build_perm_rows(modules)
        cap_map = {r["key"]: r for r in cap_rows}
        for module_key, _ in modules:
            caps = cap_map.get(module_key, {})
            can_read    = caps.get("supports_read")    and f"perm_{module_key}_read"    in request.POST
            can_write   = caps.get("supports_write")   and f"perm_{module_key}_write"   in request.POST
            can_edit    = caps.get("supports_edit")    and f"perm_{module_key}_edit"    in request.POST
            can_delete  = caps.get("supports_delete")  and f"perm_{module_key}_delete"  in request.POST
            can_approve = caps.get("supports_approve") and f"perm_{module_key}_approve" in request.POST
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


# ── Invite acceptance (magic-link first-time activation) ──────────────────────
def accept_invite(request, token):
    """
    Public endpoint — the URL emailed to a newly-created user.

    GET:  Validates the token. If valid, renders the "Set Your Password" form.
          If expired or used, shows a friendly error with instructions to ask
          for a fresh invite.
    POST: Validates passwords, sets the user's password, marks invite used,
          auto-logs the user in, redirects to dashboard.

    Note: this view is intentionally NOT @login_required — the whole point is
    that the user doesn't have credentials yet.
    """
    # If a user is already logged in, log them out first — accepting an invite
    # for account X while logged in as account Y is confusing.
    if request.user.is_authenticated:
        logout(request)

    try:
        invite = UserInvite.objects.select_related("user").get(token=token)
    except UserInvite.DoesNotExist:
        return render(request, "accounts/invite_invalid.html", {
            "reason": "This invitation link is not recognised. It may have been mistyped or already used.",
        }, status=404)

    if not invite.is_valid():
        return render(request, "accounts/invite_invalid.html", {
            "reason": (
                "This invitation has expired or already been used. "
                "Please ask your administrator to resend the invitation."
            ),
            "user_email": invite.user.email,
        }, status=410)  # 410 Gone

    if request.method == "POST":
        new_pw  = request.POST.get("new_password", "")
        confirm = request.POST.get("confirm_password", "")
        error   = None

        if len(new_pw) < 8:
            error = "Password must be at least 8 characters."
        elif new_pw != confirm:
            error = "Passwords do not match."

        if not error:
            # Activate the account
            invite.user.set_password(new_pw)
            invite.user.must_change_password = False
            invite.user.is_active = True
            invite.user.save(update_fields=["password", "must_change_password", "is_active"])

            # Mark invite consumed
            from django.utils import timezone
            invite.used    = True
            invite.used_at = timezone.now()
            invite.save(update_fields=["used", "used_at"])

            AuditLog.objects.create(
                user=invite.user, user_name=invite.user.full_name,
                action=AuditLog.ACTION_LOGIN, module="users",
                record_id=str(invite.user.pk),
                detail="Activated account via invite link and set initial password.",
            )

            # Auto-login — the user shouldn't have to type credentials right after
            # picking a password.
            login(request, invite.user)
            messages.success(
                request,
                f"Welcome, {invite.user.full_name}! Your password has been set and you are now signed in."
            )
            return redirect("dashboard")

        return render(request, "accounts/invite_accept.html", {
            "invite": invite, "error": error,
        })

    return render(request, "accounts/invite_accept.html", {"invite": invite})
