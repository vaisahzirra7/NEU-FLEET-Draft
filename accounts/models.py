from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# ─────────────────────────────────────────────────────────────
#  DEPARTMENT
# ─────────────────────────────────────────────────────────────
class Department(models.Model):
    """
    University department that owns/operates vehicles.
    Every user and every vehicle belongs to a department.
    Super Admin users can see across all departments.
    """
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Short code, e.g. 'CSC', 'TRANSPORT'")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "departments"
        ordering = ["name"]

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────
#  ROLE & PERMISSIONS
# ─────────────────────────────────────────────────────────────
class Role(models.Model):
    """
    Admin-configurable roles (e.g. Transport Manager, Fuel Clerk).
    Not hard-coded — Super Admin can create/rename/delete any role
    except the protected system Super Admin role.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(
        default=False,
        help_text="If True, this role cannot be deleted (protects Super Admin)."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


class RoleModulePermission(models.Model):
    """
    One row per module per role.
    Controls exactly what a role can do inside each module.
    The navbar and all views check these flags.
    """
    MODULE_CHOICES = [
        ("vehicles",     "Vehicle Management"),
        ("generators",   "Generator Management"),
        ("drivers",      "Driver Management"),
        ("coupons",      "Fuel Coupons"),
        ("fuel_logs",    "Fuel Logs"),
        ("maintenance",  "Maintenance"),
        ("vendors",      "Vendor Register"),
        ("reports",      "Reports"),
        ("dashboard",    "Dashboard"),
        ("users",        "User Management"),
        ("roles",        "Role Management"),
        ("audit",        "Audit Trail"),
        ("trips",        "Trips"),
        ("destinations", "Destinations"),
        ("settings",       "System Settings"),
        ("settings_email", "SMTP / Email Settings"),
    ]

    role   = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    module = models.CharField(max_length=50, choices=MODULE_CHOICES)

    can_read    = models.BooleanField(default=False)
    can_write   = models.BooleanField(default=False)
    can_edit    = models.BooleanField(default=False)
    can_delete  = models.BooleanField(default=False)
    can_approve = models.BooleanField(
        default=False,
        help_text="Approve/reject actions (currently used by Fuel Coupons; reserved for future approval workflows)."
    )

    class Meta:
        db_table = "role_module_permissions"
        unique_together = ("role", "module")
        ordering = ["role", "module"]

    def __str__(self):
        return f"{self.role.name} -> {self.module}"

    @property
    def is_read_only(self):
        return self.can_read and not (self.can_write or self.can_edit or self.can_delete or self.can_approve)

    @property
    def is_full_access(self):
        # Note: can_approve is intentionally excluded from "full access" because
        # it's an action-level grant (currently coupons-only), not a standard CRUD flag.
        return self.can_read and self.can_write and self.can_edit and self.can_delete


# ─────────────────────────────────────────────────────────────
#  CUSTOM USER
# ─────────────────────────────────────────────────────────────
class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_system_admin", True)
        return self.create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user. No self-registration — all accounts are admin-created.
    Each user has one role and one department.
    is_system_admin bypasses all module permission checks.
    """
    email       = models.EmailField(unique=True)
    full_name   = models.CharField(max_length=150)
    department  = models.ForeignKey(
        Department, on_delete=models.PROTECT, null=True, blank=True,
        related_name="users",
        help_text="Null only for system-level Super Admins spanning all departments."
    )
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, null=True, blank=True,
        related_name="users"
    )
    is_active       = models.BooleanField(default=True)
    is_staff        = models.BooleanField(default=False)
    is_system_admin = models.BooleanField(
        default=False,
        help_text="Bypasses all module permission checks. Super Admin only."
    )
    must_change_password = models.BooleanField(
        default=False,
        help_text="Forces user to change password on next login."
    )
    created_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="created_users"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    def has_module_perm(self, module, perm="read"):
        """
        Check if this user can perform `perm` on `module`.
        perm values: "read", "write", "edit", "delete"
        Usage: request.user.has_module_perm("coupons", "write")
        """
        if self.is_system_admin:
            return True
        if not self.role:
            return False
        try:
            mp = self.role.permissions.get(module=module)
            return getattr(mp, f"can_{perm}", False)
        except RoleModulePermission.DoesNotExist:
            return False

    def get_allowed_modules(self):
        """Returns list of module names this user can read (for navbar)."""
        if self.is_system_admin:
            return [m[0] for m in RoleModulePermission.MODULE_CHOICES]
        if not self.role:
            return []
        return list(
            self.role.permissions.filter(can_read=True).values_list("module", flat=True)
        )

    @property
    def can_approve_coupons(self):
        """Convenience for templates — used to show the Pending Coupons nav item."""
        return self.has_module_perm("coupons", "approve")


class PasswordResetOTP(models.Model):
    """Single-use OTP for password reset. Expires after 15 minutes."""
    user       = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="reset_otps")
    otp        = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    used       = models.BooleanField(default=False)

    class Meta:
        db_table = "password_reset_otps"

    def is_valid(self):
        from django.utils import timezone
        from datetime import timedelta
        if self.used:
            return False
        return timezone.now() < self.created_at + timedelta(minutes=15)


class UserInvite(models.Model):
    """
    Magic-link invite for new user activation.

    Workflow:
      1. Admin creates a user via /auth/users/create/ — user account exists
         but has no usable password (set_unusable_password() at create-time).
      2. A UserInvite row is created with a random 48-char token.
      3. An email is sent containing /auth/invite/<token>/.
      4. User clicks the link within the expiry window (24 hours by default),
         lands on a "Set Your Password" page, picks a password.
      5. UserInvite.used is flipped to True; the user is auto-logged in.

    Resend semantics:
      - "Resend Invite" on the user detail page creates a NEW UserInvite row
        with a fresh token. Older un-used invites for the same user are
        marked used to prevent two valid tokens floating around.
      - Old (used or expired) rows are kept for audit trail.
    """
    EXPIRY_HOURS = 24

    user       = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="invites")
    token      = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+",
        help_text="Admin user who issued this invite (None if system-generated).",
    )
    used       = models.BooleanField(default=False)
    used_at    = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_invites"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Invite for {self.user.email} ({'used' if self.used else 'pending'})"

    def is_valid(self):
        """Token is valid if not used and not yet expired."""
        from django.utils import timezone
        from datetime import timedelta
        if self.used:
            return False
        return timezone.now() < self.created_at + timedelta(hours=self.EXPIRY_HOURS)

    @property
    def expires_at(self):
        from datetime import timedelta
        return self.created_at + timedelta(hours=self.EXPIRY_HOURS)

    @classmethod
    def issue(cls, user, created_by=None):
        """
        Create a new invite for `user`, invalidating any pending older invites.
        Returns the new invite (caller is responsible for sending the email).
        """
        import secrets
        # Invalidate any pending invites — only one valid token at a time
        cls.objects.filter(user=user, used=False).update(used=True)
        token = secrets.token_urlsafe(48)[:64]  # url-safe, ~256 bits of entropy
        return cls.objects.create(user=user, token=token, created_by=created_by)
