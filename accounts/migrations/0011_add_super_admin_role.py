from django.db import migrations


NEW_MODULES = [
    ("departments",      "Departments"),
    ("report_schedules", "Report Schedules"),
    # station_deposits was added in migration 0009 to the module list
    # implicitly (the model code referenced it), but never had a proper
    # MODULE_CHOICES entry. We're now formalizing that.
]


def add_modules_and_super_admin_role(apps, schema_editor):
    """
    1. Create or update the 'Super Admin' system role with all 5 capabilities
       on every module from the current MODULE_CHOICES (whatever is in the
       model at migrate time).
    2. Assign that role to every existing User where is_system_admin=True.
    """
    Role                  = apps.get_model("accounts", "Role")
    RoleModulePermission  = apps.get_model("accounts", "RoleModulePermission")
    User                  = apps.get_model("accounts", "User")

    # Pull module choices from the model at migration time.
    modules = [m[0] for m in RoleModulePermission._meta.get_field("module").choices]

    # 1. Get or create the Super Admin system role
    super_role, _ = Role.objects.get_or_create(
        name="Super Admin",
        defaults={
            "description":    "Full system access. Cannot be edited or deleted. Assignment automatically grants the system admin flag.",
            "is_system_role": True,
        },
    )
    # Force-set the protected flag, even if the role pre-existed
    if not super_role.is_system_role:
        super_role.is_system_role = True
        super_role.save()

    # 2. Grant Super Admin every capability on every module
    for module in modules:
        RoleModulePermission.objects.update_or_create(
            role=super_role, module=module,
            defaults={
                "can_read":    True,
                "can_write":   True,
                "can_edit":    True,
                "can_delete":  True,
                "can_approve": True,
            },
        )

    # 3. Assign Super Admin role to all existing system-admin users.
    #    This makes the role + flag consistent going forward.
    User.objects.filter(is_system_admin=True).update(role=super_role)


def reverse_(apps, schema_editor):
    """
    Reversing this migration: remove the Super Admin role.
    Users currently in it keep their is_system_admin flag (it was set
    independently before this migration).
    """
    Role = apps.get_model("accounts", "Role")
    Role.objects.filter(name="Super Admin", is_system_role=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0010_alter_rolemodulepermission_module"),
    ]

    operations = [
        # 0010 (the AlterField above) handles the column choices update.
        # This migration handles the DATA: creating the Super Admin role
        # and granting permissions.
        migrations.RunPython(add_modules_and_super_admin_role, reverse_),
    ]
