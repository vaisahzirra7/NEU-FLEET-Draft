# VanaraFleetOps — Stage 4: Trips + Destinations + Driver Payments

This drop completes the third correction from your institution review:
**recording paid trips for drivers**, with a managed destinations list and
a new report for driver payments per period.

---

## What's in this drop

### Trips app (new)

- `trips/__init__.py`, `apps.py`, `admin.py`, `models.py`, `migrations/0001_initial.py`
  — All from Stage 1 foundation. Included so the app is self-contained.
- `trips/views.py` — list, create, detail. Plus destination list/create/edit.
- `trips/urls.py` — routes for trips and destinations under `/trips/...`.

### Templates (new)

- `templates/trips/list.html` — filterable trip list with running total.
- `templates/trips/form.html` — log a trip: driver, vehicle, from/to dropdown
  with one-off free-text fallback, amount, optional fuel coupon links.
- `templates/trips/detail.html` — full trip view with linked coupons.
- `templates/destinations/list.html` — manage the destination register.
- `templates/destinations/form.html` — add/edit destination.
- `templates/reports/driver_payments.html` — new report.

### Templates (updated)

- `templates/base.html` — added "Trips" nav (Operations section) and
  "Destinations" nav (Admin section). Each is gated by the matching permission.
- `templates/reports/index.html` — added Driver Payments card.
- `templates/drivers/form.html` — added Payment Type field below Status.

### Backend (updated)

- `drivers/views.py` — driver create/edit now persist `payment_type` and
  pass `Driver.PAYMENT_CHOICES` to templates.
- `reports/views.py` — added `driver_payments` view: filterable by date,
  driver, payment type. Aggregates per driver with trip count and total.
- `reports/urls.py` — added `/reports/driver-payments/`.

---

## How to apply

1. **No new database migrations.** The trips schema was already created
   in Stage 1 (`trips.0001_initial`). If for some reason `showmigrations trips`
   shows it as unapplied, run `python manage.py migrate trips`.

2. **Important — fix `config/urls.py`.** If you previously deleted the
   `path("trips/", include("trips.urls"))` line to make the server boot,
   add it back. Trips URLs only work if it's there:

   ```python
   path("trips/", include("trips.urls")),
   ```

3. Drop these files into your project, overwriting where applicable.

4. Restart the server.

5. Grant permissions:
   - **trips** module: read/write for users who log trips, plus the rest
     of the permission matrix as needed.
   - **destinations** module: read for everyone who logs trips (so they
     can see the dropdown), write/edit for admins who maintain the list.
   - **reports** module: read users can now access the new Driver Payments
     report alongside the existing reports.

6. Seed some destinations: Admin > Destinations > Add. Until you do, the
   trip form will only show free-text inputs in the From/To fields.

7. Test:
   - Drivers > Add new driver > verify the Payment Type field appears.
   - Trips > Log Trip > submit one with a managed destination and one with
     free text. Both should save.
   - Reports > Driver Payments > confirm the totals match what you logged.

---

## What I'm flagging honestly

1. **Trips are not immutable like maintenance records.** I built only
   create + read; there's no edit or delete view. If you want trips to be
   editable (or strictly immutable), tell me. Right now a trip can't be
   changed once logged, but that's by omission, not design.

2. **The "From/To dropdown OR free-text" UI is friendly but ambiguous.**
   If a user fills BOTH the dropdown and the free-text field for the same
   side, the view picks the dropdown and silently discards the free text.
   The form hint says this, but a user who isn't paying attention won't
   notice. JS could disable one when the other is used; I didn't add it.

3. **No CSV/PDF export for driver payments.** Existing reports have export
   buttons; this one doesn't. I judged it not essential for v1. Easy to add
   later by copying the pattern from `maintenance_report`.

4. **The coupon picker in trip form is limited to 100 most recent.** If you
   have a vehicle with hundreds of coupons over time, older ones won't show.
   This is intentional to keep the form fast. If a user can't find a coupon,
   they can leave the M2M blank.

5. **`payment_type` defaults to `salaried` for all existing drivers**
   (from the Stage 1 migration default). Update each driver record to
   `per_trip` or `mixed` where appropriate. There's no bulk update tool.

6. **Department scoping uses `vehicle__department`.** A trip belongs to a
   department through its vehicle. If you ever assign drivers to departments
   independently of vehicles, this will need rethinking.

7. **No "Edit Destination" link from the Trips form.** If an admin needs to
   add a new destination mid-trip-log, they have to abandon the form and
   navigate to Destinations. Could be improved with a modal or a small
   "+ Add destination" link, but didn't seem critical.

8. **Same caveats as before:** still no tests, SECRET_KEY and DB password
   still in `settings.py` rather than `.env`.

---

## Permissions summary (now you have the full matrix)

| Module        | Read | Write | Edit | Delete | Approve |
|---------------|------|-------|------|--------|---------|
| vehicles      | ✓    | ✓     | ✓    | ✓      |         |
| drivers       | ✓    | ✓     | ✓    | ✓      |         |
| coupons       | ✓    | ✓     | ✓    | ✓      | ✓       |
| fuel_logs     | ✓    | ✓     | ✓    | ✓      |         |
| maintenance   | ✓    | ✓     |      |        |         |
| **trips**     | ✓    | ✓     |      |        |         |
| **destinations** | ✓ | ✓     | ✓    |        |         |
| vendors       | ✓    | ✓     | ✓    | ✓      |         |
| reports       | ✓    |       |      |        |         |
| dashboard     | ✓    |       |      |        |         |
| users         | ✓    | ✓     | ✓    | ✓      |         |
| roles         | ✓    | ✓     | ✓    | ✓      |         |
| audit         | ✓    |       |      |        |         |

(Edit/Delete on trips and maintenance is intentionally absent — both are
treated as immutable records.)
