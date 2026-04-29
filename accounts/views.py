from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import User, Role, RoleModulePermission, Department


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
        logout(request)
    return redirect("accounts:login")


# ── User Management ───────────────────────────────────────────
@login_required
def users_list(request):
    if not request.user.has_module_perm("users", "read"):
        return HttpResponseForbidden(render(request, "403.html"))

    users = User.objects.select_related("role", "department").order_by("full_name")
    return render(request, "accounts/users_list.html", {"users": users})


@login_required
def user_create(request):
    if not request.user.has_module_perm("users", "write"):
        return HttpResponseForbidden()

    roles       = Role.objects.all()
    departments = Department.objects.filter(is_active=True)

    if request.method == "POST":
        full_name  = request.POST.get("full_name", "").strip()
        email      = request.POST.get("email", "").strip()
        password   = request.POST.get("password", "")
        role_id    = request.POST.get("role")
        dept_id    = request.POST.get("department")

        errors = {}
        if not full_name: errors["full_name"] = "Full name is required."
        if not email:     errors["email"]     = "Email is required."
        if not password:  errors["password"]  = "Password is required."
        if not role_id:   errors["role"]      = "Please select a role."
        if User.objects.filter(email=email).exists():
            errors["email"] = "A user with this email already exists."

        if not errors:
            user = User.objects.create_user(
                email=email, full_name=full_name, password=password,
                role_id=role_id or None,
                department_id=dept_id or None,
                created_by=request.user
            )
            messages.success(request, f"User '{user.full_name}' created successfully.")
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
        user.full_name     = request.POST.get("full_name", user.full_name).strip()
        user.role_id       = request.POST.get("role") or None
        user.department_id = request.POST.get("department") or None
        user.is_active     = request.POST.get("is_active") == "on"
        new_pw             = request.POST.get("password", "")
        if new_pw:
            user.set_password(new_pw)
        user.save()
        messages.success(request, f"User '{user.full_name}' updated.")
        return redirect("accounts:users")

    return render(request, "accounts/user_form.html", {
        "obj": user, "roles": roles, "departments": departments
    })


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
            return render(request, "accounts/role_form.html", {"modules": modules, "post": request.POST})

        role = Role.objects.create(name=name, description=description)

        # Save permissions for each module
        for module_key, _ in modules:
            can_read   = f"perm_{module_key}_read"   in request.POST
            can_write  = f"perm_{module_key}_write"  in request.POST
            can_edit   = f"perm_{module_key}_edit"   in request.POST
            can_delete = f"perm_{module_key}_delete" in request.POST
            if can_read or can_write or can_edit or can_delete:
                RoleModulePermission.objects.create(
                    role=role, module=module_key,
                    can_read=can_read, can_write=can_write,
                    can_edit=can_edit, can_delete=can_delete,
                )

        messages.success(request, f"Role '{role.name}' created.")
        return redirect("accounts:roles")

    return render(request, "accounts/role_form.html", {"modules": modules})


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
            can_read   = f"perm_{module_key}_read"   in request.POST
            can_write  = f"perm_{module_key}_write"  in request.POST
            can_edit   = f"perm_{module_key}_edit"   in request.POST
            can_delete = f"perm_{module_key}_delete" in request.POST
            if can_read or can_write or can_edit or can_delete:
                RoleModulePermission.objects.create(
                    role=role, module=module_key,
                    can_read=can_read, can_write=can_write,
                    can_edit=can_edit, can_delete=can_delete,
                )

        messages.success(request, f"Role '{role.name}' updated.")
        return redirect("accounts:roles")

    return render(request, "accounts/role_form.html", {
        "obj": role, "modules": modules, "perms": perms
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
