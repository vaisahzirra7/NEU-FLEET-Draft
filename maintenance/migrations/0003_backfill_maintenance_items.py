"""
Data migration: backfill MaintenanceItem rows from existing MaintenanceRecord data.

Before this migration: each MaintenanceRecord held a single (service_type,
description, total_cost) triple directly on the record.

After this migration: that data lives in a MaintenanceItem child row.
The record's total_cost is recalculated from items (and will equal the
original total_cost for records with one item).

Safe to run on production data. Idempotent: skips records that already
have an item.
"""
from decimal import Decimal
from django.db import migrations


def backfill_items(apps, schema_editor):
    MaintenanceRecord = apps.get_model("maintenance", "MaintenanceRecord")
    MaintenanceItem   = apps.get_model("maintenance", "MaintenanceItem")

    for rec in MaintenanceRecord.objects.all():
        if MaintenanceItem.objects.filter(record=rec).exists():
            continue
        MaintenanceItem.objects.create(
            record       = rec,
            service_type = rec.service_type or "other",
            description  = (rec.description or "Migrated record")[:255],
            cost         = rec.total_cost or Decimal("0.00"),
        )


def reverse_backfill(apps, schema_editor):
    MaintenanceRecord = apps.get_model("maintenance", "MaintenanceRecord")
    MaintenanceItem   = apps.get_model("maintenance", "MaintenanceItem")
    for rec in MaintenanceRecord.objects.all():
        items = MaintenanceItem.objects.filter(record=rec)
        if items.count() == 1:
            items.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0002_alter_maintenancerecord_description_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_items, reverse_code=reverse_backfill),
    ]
