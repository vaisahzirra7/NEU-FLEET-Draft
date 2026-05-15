"""
Replace the Generator.department FK with a free-text 'building' field.

Three-step migration (single file, runs atomically):
  1. Add 'building' column as nullable.
  2. Backfill: copy each generator's department name into 'building'.
  3. Drop the 'department' FK and make 'building' non-null.
"""
from django.db import migrations, models


def backfill_building_from_department(apps, schema_editor):
    """Copy department.name into the new building field for every existing row."""
    Generator = apps.get_model("generators", "Generator")
    for gen in Generator.objects.all():
        # gen.department is still accessible at this point — the FK is dropped later
        if gen.department_id and not gen.building:
            gen.building = gen.department.name
            gen.save(update_fields=["building"])


def reverse_noop(apps, schema_editor):
    """
    Reverse is a no-op: the department FK was dropped. If you reverse this
    migration, the building text is preserved but department becomes empty.
    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("generators", "0002_generator_needs_monthly_fuel"),
    ]

    operations = [
        # 1. Add nullable building column
        migrations.AddField(
            model_name="generator",
            name="building",
            field=models.CharField(
                max_length=150, null=True, blank=True,
                help_text="Name of the building this generator serves, e.g. 'Library', 'Senate Block'.",
            ),
        ),
        # 2. Backfill from department.name
        migrations.RunPython(backfill_building_from_department, reverse_noop),
        # 3. Drop the department FK
        migrations.RemoveField(
            model_name="generator",
            name="department",
        ),
        # 4. Make building non-null now that data exists
        migrations.AlterField(
            model_name="generator",
            name="building",
            field=models.CharField(
                max_length=150,
                help_text="Name of the building this generator serves, e.g. 'Library', 'Senate Block'.",
            ),
        ),
    ]
