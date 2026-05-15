================================================================================
   Gen-3: Maintenance accepts Generators
================================================================================

This drop wires generators into the maintenance lifecycle. Mirrors Gen-2 for
coupons, but simpler — maintenance has no driver field, no approval workflow.

The Stage 3 multi-line item structure stays intact; only the parent record
changes.

--------------------------------------------------------------------------------
APPLY (do not skip the cache wipe)
--------------------------------------------------------------------------------

1. Stop runserver (Ctrl+C).

2. From project root:
     Expand-Archive -Path .\gen3.zip -DestinationPath . -Force

3. Wipe Python caches:
     Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force

4. Apply the migration:
     python manage.py migrate

   You should see exactly one new migration applied:
     Applying maintenance.0004_maintenance_generator_support... OK

5. Hard-refresh the browser to pick up the updated CSS (Ctrl+Shift+R).

6. Start the server:
     python manage.py runserver

--------------------------------------------------------------------------------
WHAT CHANGED — MODEL & DB
--------------------------------------------------------------------------------

MaintenanceRecord
  * vehicle is now nullable
  * NEW: generator FK (nullable)
  * NEW constraint: exactly one of vehicle/generator must be set
  * NEW helpers: is_for_vehicle, is_for_generator, asset, asset_label, asset_kind
  * __str__ uses asset_label safely (won't crash on generator records)

Service-type choices (both MaintenanceRecord and MaintenanceItem)
  * NEW option: "General Service" (value: general_service)
  * Existing categories unchanged. Use general_service for generator service
    or anything that doesn't fit the more specific categories.

MaintenanceItem — no model changes (the line-item structure stays the same).

--------------------------------------------------------------------------------
WHAT CHANGED — UI
--------------------------------------------------------------------------------

Log Maintenance form
  * NEW asset toggle at the top: Vehicle / Generator
  * Vehicle path: existing vehicle dropdown (unchanged)
  * Generator path: generator dropdown + read-only Building field
    (auto-filled from selected generator)
  * Service date moved out of the asset row so it's shared by both modes
  * Line items table unchanged — same multi-row workflow

Maintenance list
  * "Vehicle" column renamed to "Asset"
  * Each row shows a tinted vehicle/generator pill before the plate/tag link
  * Search now matches generator tag and name
  * Page subtitle updated to "vehicle and generator service / repair history"

Maintenance detail
  * Header and breadcrumb show the asset label (plate OR tag)
  * Info table shows Vehicle row for vehicle records, Generator + Building
    rows for generator records
  * "Back to Vehicle" / "Back to Generator" button routes appropriately

main.css
  * Asset-toggle CSS moved from per-template inline blocks to global rules
    (.asset-toggle, .toggle-pill). This means it now works on the maintenance
    form without copying styles in.
  * Old per-template inline copies still exist in the coupon templates but
    are redundant (last definition wins; no conflict).

--------------------------------------------------------------------------------
PERMISSIONS / SCOPING
--------------------------------------------------------------------------------

maintenance/dept_filter was rewritten as a Q-object filter (same pattern as
coupons and fuel_logs in Gen-2):

  - Vehicle maintenance records: still scoped to user's department via
    vehicle.department FK.
  - Generator maintenance records: NOT department-scoped. Any user with
    maintenance read permission sees all generator maintenance records.

Consistent with Gen-1/Gen-2 decisions that generators are organisation-wide.

--------------------------------------------------------------------------------
WHAT GEN-3 DOES NOT TOUCH
--------------------------------------------------------------------------------

  * Reports — generator spending report and monthly-expense update is Gen-4.
    The existing maintenance report will silently exclude generator records
    until Gen-4. Vehicle-only totals are still accurate.
  * Vendor report breakdowns by asset type — Gen-4.
  * Coupons, fuel logs, trips, generators app — unchanged.

--------------------------------------------------------------------------------
KNOWN FLAGS
--------------------------------------------------------------------------------

1. Maintenance records are immutable (no edit view). This was a Stage 3
   decision and Gen-3 preserves it. If you log a maintenance record for the
   wrong asset (e.g. picked vehicle when it should have been generator), the
   only fix today is through the Django admin or DB. Tell me if that's
   unworkable and we'll add an edit view later.

2. The "general_service" choice is now available everywhere, including for
   existing vehicle maintenance forms. That's fine — it just means vehicle
   users have one more option in the dropdown. No data migration needed for
   existing records.

3. The vehicle filter URL param (?vehicle=...) on the list page still works
   but only filters vehicle records. There's no equivalent ?generator=...
   param yet. Easy to add if needed.

4. The maintenance/dashboard "service due soon" alert (next_service_date
   within 14 days) currently looks across both asset types. Generator
   records with next_service_date set will appear in that alert too. If you
   want generator service alerts surfaced separately on the Generators page,
   that's a follow-up.

================================================================================
TEST SEQUENCE
================================================================================

  1. Open /maintenance/new/ — toggle defaults to Vehicle, existing flow works.
  2. Click Generator toggle — fields swap. Pick a generator; Building
     auto-fills (read-only).
  3. Add 2-3 line items including one with service_type "General Service".
     Submit. Should redirect to that generator's detail page (in the
     generators module, NOT vehicles).
  4. Browse to /maintenance/ — the new record should appear with an amber
     "GENERATOR" pill. Search by the generator's tag — should find it.
  5. Click the row — detail page should show Generator and Building rows,
     not Vehicle.
  6. Log another vehicle maintenance record to confirm the vehicle path
     still works.
  7. (Constraint check) Try to log without picking an asset (toggle defaults
     to vehicle but leave the dropdown empty) — should show field-level
     error, not a database crash.

================================================================================
