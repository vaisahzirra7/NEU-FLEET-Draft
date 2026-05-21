================================================================================
   Permissions Audit + Fix
================================================================================

I went through the full codebase looking for:
  1. Role-form grid issues (the screenshot question you asked)
  2. Unprotected views (the security audit you asked me to do)

Found four real bugs. Three are security; one is UX/integrity.

--------------------------------------------------------------------------------
APPLY
--------------------------------------------------------------------------------

1. Stop runserver.
2. Expand-Archive -Path .\perms_audit.zip -DestinationPath . -Force
3. Get-ChildItem -Path . -Recurse -Filter "__pycache__" -Directory | Remove-Item -Recurse -Force
4. python manage.py runserver
5. Hard-refresh browser.

No migrations.

--------------------------------------------------------------------------------
WHAT'S FIXED
--------------------------------------------------------------------------------

FIX 1 — Role form: dead checkboxes removed
   Before: Dashboard, Reports, Audit Trail rows all had Read/Write/Edit/
           Delete checkboxes. Only Read was ever checked by any view; the
           other three were dead — ticking them did nothing.
   After:  Each module declares which permissions are meaningful (a
           MODULE_CAPABILITIES dict in accounts/views.py). Unsupported
           permissions render as "—" (same treatment Approve already had).
           Server also enforces the matrix on save, so a malicious POST
           can't sneak through an unsupported permission.

   Modules with their real capabilities:
     vehicles:       Read/Write/Edit/Delete
     generators:     Read/Write/Edit/Delete
     drivers:        Read/Write/Edit/Delete
     coupons:        Read/Write/Edit/Delete/Approve
     fuel_logs:      Read/Write
     maintenance:    Read/Write/Edit
     vendors:        Read/Write/Edit/Delete
     reports:        Read
     dashboard:      Read
     users:          Read/Write/Edit
     roles:          Read/Write/Edit/Delete
     audit:          Read
     trips:          Read/Write/Edit
     destinations:   Read/Write/Edit
     settings:       Read/Edit
     settings_email: Read/Edit

   Legend below the table updated to explain the dashes.

FIX 2 — vehicles.dismiss_fuel_reminder
   Before: Any logged-in user could dismiss any vehicle's reminder. Only
           @login_required was applied; no module-permission check, no
           department scoping.
   After:  Requires vehicles:edit. Department-scoped via dept_filter, so
           a non-admin can only dismiss their own department's vehicles.

FIX 3 — coupons.print_slip
   Before: @login_required only. Used dept_filter to restrict WHICH
           coupons could be printed, but never checked that the user
           had any coupon permission at all. A user with NO coupon
           access could navigate to /coupons/print/<id>/ and print.
   After:  Requires coupons:read in addition to dept scoping.

FIX 4 — coupons.lookup_ajax  (THIS WAS THE BIGGEST)
   Before: @login_required only. No permission check. No department
           scoping. Any logged-in user could GET /coupons/lookup/?q=<id>
           and receive back full coupon details: driver name, plate,
           generator tag, station, total value, litres, purpose.
           Information disclosure across the whole organisation.
   After:  Requires fuel_logs:write (the perm needed to actually use
           this endpoint legitimately). Returns 403 JSON otherwise.

--------------------------------------------------------------------------------
WHAT I CHECKED AND DID NOT FIND ISSUES WITH
--------------------------------------------------------------------------------

  * Every view in vehicles, generators, drivers, vendors, fuel_logs,
    maintenance, reports, trips, system_settings, audit checks the
    right permission for what it does.
  * Sidebar navigation is consistently gated by "X in modules" — a user
    can't see nav links to modules they don't have read access to.
  * dept_filter is applied consistently to coupons, fuel_logs,
    maintenance, and trips for non-admin users.
  * has_module_perm() correctly bypasses for is_system_admin and denies
    for users with no role.
  * Public endpoints (login, password_reset_*, accept_invite) are
    correctly UNauthenticated. Each validates internally (e.g. invite
    token expiry, OTP validity).

--------------------------------------------------------------------------------
WHAT I DELIBERATELY DID NOT TOUCH
--------------------------------------------------------------------------------

  * accounts.change_password — no module check, but it's the user
    changing THEIR OWN password. Correct as-is.

  * accounts.profile_view — same logic. The user views/edits their own
    profile. No module check needed.

  * The Approve column on Fuel Coupons. It correctly only shows up for
    coupons because that's the only module with an approval workflow.
    The MODULE_CAPABILITIES dict makes adding approve to other modules
    later a one-line change.

--------------------------------------------------------------------------------
RECOMMENDED FURTHER WORK (not done in this drop)
--------------------------------------------------------------------------------

  1. Audit logging for permission denials. Right now if someone tries
     to access a forbidden URL, they get a 403 but no audit entry.
     For a security-sensitive system you may want to record failed
     access attempts.

  2. Rate limiting on lookup_ajax. Even with the permission fix, a
     Fuel Clerk could enumerate coupon IDs at the rate their bandwidth
     allows. Adding a per-user rate limit (e.g. 30 lookups per minute)
     would prevent enumeration.

  3. CSRF protection is on by default for POST. Confirm any JSON
     endpoints that accept POST also have CSRF (lookup_ajax is GET so
     it's fine).

  4. The "must_change_password" flag combined with the Emergency
     default-password fallback means a determined admin can still
     hand out shared known passwords. Not a vulnerability per se,
     but worth a policy decision.

  5. There's no per-USER override of role permissions. If a single
     user needs an exception, you have to either give their whole
     role the permission or create a one-person role. Not urgent
     but a real limitation.

--------------------------------------------------------------------------------
TEST SEQUENCE
--------------------------------------------------------------------------------

  1. /auth/roles/create/ — confirm the grid now shows "—" instead of
     checkboxes for Dashboard/Audit Trail/Reports under Write/Edit/Delete.

  2. Try to tick all 5 checkboxes on Dashboard via browser inspector
     (uncheck the disabled attr first). Save. Reopen the role.
     - Only Read should be set. Write/Edit/Delete silently ignored.

  3. Create a "Test Driver" role with NO coupon access. Log in as a
     user with that role. Navigate manually to /coupons/print/1/ (or
     any coupon ID). Should get 403 Forbidden.

  4. Same user, try the coupon lookup. From DevTools console:
        fetch('/coupons/lookup/?q=COUP-001').then(r => r.json()).then(console.log)
     Should return {error: "Permission denied."} with HTTP 403.

  5. Same user, go to dashboard. Try clicking "Dismiss" on any fuel
     reminder. Should get 403.

  6. Grant the role coupons:read. Re-test step 3 — should now print.
     Re-test step 5 — should still fail (needs vehicles:edit).

================================================================================
