================================================================================
   Dashboard — Generator Support
================================================================================

Two files. Bug fixes + UI additions.

--------------------------------------------------------------------------------
APPLY
--------------------------------------------------------------------------------

1. Stop runserver.
2. Expand-Archive -Path .\dashboard_fix.zip -DestinationPath . -Force
3. Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
4. python manage.py runserver
5. Hard-refresh browser

No migrations.

--------------------------------------------------------------------------------
BUGS FIXED (data correctness)
--------------------------------------------------------------------------------

  * Coupons Issued Today, Open Coupons: were excluding generator coupons for
    non-admin (dept-scoped) users. Now use the same Q-pattern widening as
    coupons/views.py — vehicle records stay dept-scoped, generator records
    are organisation-wide.

  * Spend This Month: same fix. Was silently dropping generator fuel +
    generator maintenance for dept-scoped users. As Super Admin you saw
    the correct combined number; non-admins did not.

  * Service Due Soon: was using {% v.plate_number %} on MaintenanceRecord
    objects. This would have crashed the moment a vehicle had a
    next_service_date set. Either no one ever set one or the empty-state
    saved you. Either way, fixed — now asset-aware.

--------------------------------------------------------------------------------
NEW UI
--------------------------------------------------------------------------------

  * Active Generators KPI card next to Active Vehicles. Amber bolt icon.
    Shown when user has generators:read permission.

  * Spend This Month subtitle now shows asset breakdown when there's
    generator spend in the month:
        V: ₦95,000 · G: ₦12,000
    instead of "Fuel + Maintenance". Vehicle figure in blue, generator
    figure in amber, matching the asset-label palette.

  * Service Due Soon: each row shows a Vehicle / Generator label below the
    plate/tag (same label-below pattern as the list pages). Empty state
    text changed from "No vehicles due for service" to "No assets due for
    service."

--------------------------------------------------------------------------------
NOT INCLUDED (intentional)
--------------------------------------------------------------------------------

  * "Monthly fuel reminders" panel: still vehicle-only. Generators with
    needs_monthly_fuel=True don't surface here. Asked you about this
    before; you didn't say yes, so I left it. Tell me if you want it.

  * "Top 5 by Cost (This Month)": stays vehicle-only. Generators have
    their own breakdown via the Per-Generator Spending report. Adding
    a parallel "Top Generators" panel feels like clutter when there are
    only 2-3 of them.

--------------------------------------------------------------------------------
KNOWN BEHAVIOR — FLEET SUMMARY EMAIL
--------------------------------------------------------------------------------

The Fleet Summary email schedules still group spend by department.
Generators have no department so they don't appear in dept rows BUT do
count in grand totals — meaning the dept-breakdown rows won't sum to the
grand total when generator activity exists. I asked you about adding a
synthetic "Generators (org-wide)" row to that table earlier and didn't
get a decision. Tell me yes or no and I'll do it in 5 minutes.

================================================================================
