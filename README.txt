================================================================================
   Mobile Responsiveness — Phase 1
================================================================================

Five files. Adds:
  - Global mobile CSS (page padding, filter bars wrap, headings shrink)
  - The .table-responsive opt-in pattern (tables turn into stacked cards on phones)
  - Pattern applied to: vehicles, drivers, vendors list pages

--------------------------------------------------------------------------------
APPLY
--------------------------------------------------------------------------------

1. Stop runserver.
2. Expand-Archive -Path .\mobile_responsive.zip -DestinationPath . -Force
3. Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
4. python manage.py runserver
5. Hard-refresh browser.

--------------------------------------------------------------------------------
WHAT TO TEST
--------------------------------------------------------------------------------

Open the dashboard in Chrome DevTools, hit F12, click the device toolbar
icon, switch to iPhone or similar. Then visit:

  /vehicles/   → table should turn into stacked cards. Each card shows
                 "Plate Number: GMB-217-AA" on its own line, then "Type:
                 Bus" on the next, etc. View and Edit buttons at the
                 bottom, full-width.

  /drivers/    → same treatment. Each driver becomes a card.

  /vendors/    → same.

Resize the browser between phone and desktop sizes — the layout should
flip cleanly at 640px.

Also test:
  - Filter bars on every list page wrap nicely on phone (controls go
    full-width and stack)
  - Page headers stack title above buttons on phone
  - Dashboard tile values still fit (smaller font on tiny screens)

--------------------------------------------------------------------------------
WHAT'S NOT YET DONE
--------------------------------------------------------------------------------

The .table-responsive class is only applied to vehicles, drivers, and
vendors. Other list pages still horizontal-scroll on mobile (functional
but ugly):

  - coupons/list.html  (and pending_list.html, redeemed list)
  - fuel_logs/list.html
  - maintenance/list.html
  - trips/list.html
  - station_deposits/list.html
  - generators/list.html
  - audit/list.html
  - reports/* (lower priority since reports are mostly desktop)

To apply the pattern to any of these, follow the same recipe:
  1. Change `<table class="data-table">` to `<table class="data-table table-responsive">`
  2. For each <td>, add data-label="<the header text from the column>"
  3. For the action cell (View/Edit/Delete buttons), add data-label=""
     and class="actions-cell"

If you'd rather I do the rest in a follow-up drop, just say the word and
I'll batch them.

--------------------------------------------------------------------------------
HOW THE .table-responsive CLASS WORKS (for future maintenance)
--------------------------------------------------------------------------------

Below 640px viewport width:
  - <thead> is hidden (column labels move into each cell via data-label)
  - <tr> becomes a bordered card with shadow
  - <td> becomes a flex row: label on left, value on right
  - Action cells with data-label="" get a top border separator and
    buttons take full width side-by-side

Above 640px:
  - Behaves like a normal table. No visual change.

The data-label attribute is read by CSS via attr(). If you forget to
add data-label="..." to a <td>, that cell will just show its value
with no label prefix.

================================================================================
