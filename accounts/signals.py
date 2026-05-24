"""
Keep User.is_system_admin in sync with the user's role assignment.

Rule:
  - If a user is assigned the "Super Admin" system role → is_system_admin=True
  - If a user is REMOVED from that role (assigned a different role or no role) → is_system_admin=False

This makes the Super Admin role the single source of truth for system-wide
access. The flag is preserved for fast permission checks via has_module_perm.
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import User, Role


@receiver(pre_save, sender=User)
def sync_super_admin_flag(sender, instance, **kwargs):
    """
    Before saving the User, check whether their role is Super Admin and
    flip is_system_admin accordingly.

    Why pre_save and not post_save?
        We want the User row to be saved with the correct flag in a single
        DB write, not a save followed by an update. pre_save mutates the
        instance before it's written.
    """
    # Resolve the Super Admin role. If it doesn't exist yet (first migrate
    # or fresh DB), skip — nothing to sync against.
    try:
        super_role = Role.objects.get(name="Super Admin", is_system_role=True)
    except Role.DoesNotExist:
        return

    if instance.role_id == super_role.pk:
        instance.is_system_admin = True
    else:
        # Don't auto-demote during the initial superuser bootstrap (when
        # is_system_admin is being set explicitly but the role hasn't been
        # assigned yet). We can detect this by checking if the row is new.
        if instance.pk is None and instance.is_system_admin:
            # New user being created with is_system_admin already True
            # — assume the caller knows what they're doing (e.g. createsuperuser).
            # Their role will be reconciled when they're given one.
            return
        instance.is_system_admin = False
