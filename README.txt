================================================================================
   Permissions Overhaul — Add 3 modules, lock Super Admin role
================================================================================

Eight files. One data migration.

This drop closes the gaps you identified in roles & permissions:

  - Add 3 modules to the role grid: Departments, Report Schedules,
    and Fuel Station Deposits (the third was an earlier slip on my part).
  - Schedule actions (Edit / Send Now / Delete) now check the new
    `report_schedules` module instead of `reports`.
  - Departments page now permission-aware instead of Super-Admin-only.
  - New system-locked "Super Admin" role created via migration.
  - Assigning the Super Admin role to a user automatically grants
    is_system_admin=True (single source of truth).
  - Existing custom roles (Administrator, Quality Assurance, Transport
    Officer) are NOT auto-modified — you'll need to grant the new
    permissions manually if you want them.

--------------------------------------------------------------------------------
APPLY
--------------------------------------------------------------------------------

1. Stop runserver.
2. Expand-Archive -Path .\perms_overhaul.zip -DestinationPath . -Force
3. Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
4. python manage.py migrate

   You should see:
     Applying accounts.0010_add_super_admin_role... OK

5. python manage.py runserver
6. Hard-refresh.

What the migration does:
  - Creates the "Super Admin" Role with is_system_role=True
  - Grants it all 5 permissions on every module
  - Assigns it to all existing users with is_system_admin=True (yourself
    included). You won't lose access.

--------------------------------------------------------------------------------
WHAT'S NEW IN THE ROLE GRID
--------------------------------------------------------------------------------

Three new rows appear in /auth/roles/create/ and /auth/roles/<id>/edit/:

  Departments        → Read, Write, Edit, Delete
  Report Schedules   → Read, Write, Edit, Delete
  Fuel Station Deposits → Read, Write, Delete (no Edit, deposits are immutable)

--------------------------------------------------------------------------------
WHAT'S NEW IN THE SIDEBAR
--------------------------------------------------------------------------------

  - Departments link: now visible to any user with `departments:read`,
    not just Super Admin. (Previously hard-coded Super-Admin-only.)
  - Report Schedules link: now visible to any user with
    `report_schedules:read`, not just users with `reports:read`.

--------------------------------------------------------------------------------
SUPER ADMIN ROLE BEHAVIOR
--------------------------------------------------------------------------------

The Super Admin role is now a SYSTEM ROLE (is_system_role=True). It appears
in the roles list with "Protected" status. Attempting to edit or delete it
via the UI shows a "System roles cannot be modified" error.

The role is also TIED to the User.is_system_admin flag via a signal:

  - Assigning the Super Admin role to a user → is_system_admin = True
    (granted automatically on save)
  - Removing the Super Admin role from a user → is_system_admin = False
    (revoked automatically on save)

This means: removing someone from the Super Admin role immediately demotes
them from system-wide access. This is by design — the role IS the
permission. But it does mean a casual role change could lock somebody out
of admin functions. Always have at least one other Super Admin before
demoting someone.

--------------------------------------------------------------------------------
WHAT'S NOT CHANGED
--------------------------------------------------------------------------------

  - Existing custom roles (Administrator, Quality Assurance, Transport
    Officer) keep their EXACT current permissions. Nothing added, nothing
    removed. If you want the Administrator role to manage departments or
    schedules, you'll need to tick those boxes manually.
  - Existing users with role assignments unchanged.
  - The "Save Changes" button on the Super Admin role page is suppressed
    server-side (was already suppressed in template before this drop).

--------------------------------------------------------------------------------
TESTS BEFORE TRUSTING THIS
--------------------------------------------------------------------------------

  1. /auth/roles/ → "Super Admin" appears in the list with "System" type
     badge. No Edit button (it's protected). Description reads "Full
     system access. Cannot be edited or deleted..."

  2. As Super Admin, go to /auth/users/<your-pk>/edit/. Your role
     should now be "Super Admin". You still have all access.

  3. Try to edit the Super Admin role itself (e.g. /auth/roles/<id>/edit/).
     The form loads but submitting POST shows "System roles cannot be
     modified" and redirects back.

  4. Create a NEW user, assign the Administrator role, log in as them:
     - Should NOT see Departments link (unless you've granted it)
     - Should NOT see Send Now / Edit / Delete on Report Schedules
       (unless you've granted those new modules)
     - Should see the standard Administrator capabilities

  5. As Super Admin, edit the Administrator role. Tick the new
     "Departments" and "Report Schedules" modules with all capabilities.
     Save. Log back in as the Administrator user — they should now see
     Departments in the sidebar and full schedule actions.

  6. Now demote that Administrator user: change their role to "Quality
     Assurance". Save. Log in as them — should be locked out of
     everything Administrator could do, restricted to QA scope.

  7. (Optional) Migration sanity: from `python manage.py shell`:
        from accounts.models import User, Role
        sr = Role.objects.get(name="Super Admin")
        for u in User.objects.filter(is_system_admin=True):
            assert u.role_id == sr.pk, f"{u} is system admin but not in Super Admin role"
        print("All system admins are in Super Admin role")

--------------------------------------------------------------------------------
HONEST CAVEATS
--------------------------------------------------------------------------------

* The signal flips is_system_admin on pre_save. If you create a user via
  the Django shell with `User.objects.create(..., is_system_admin=True,
  role=some_non_super_role)`, the signal will OVERRIDE your flag back to
  False because the role isn't Super Admin. This is correct behavior but
  worth knowing.

* `createsuperuser` (the management command) sets is_system_admin=True
  on a user with no role. The signal detects this (pk is None on create
  + is_system_admin already True) and skips the override. The new user
  is a Super Admin (flag True) but has no role assigned. You should then
  manually assign them the Super Admin role via /auth/users/.

* The "Administrator" role (custom, not system) still shows muted green
  badges on the roles list because it doesn't have FULL access on every
  module — Reports has only Read available, for example, so it's never
  "full access" for that module. The badge color is determined by
  is_full_access (all 4 caps true), which isn't possible for Reports.
  This is correct and expected.

================================================================================
