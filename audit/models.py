from django.db import models


class AuditLog(models.Model):
    """
    Append-only log of key system actions.
    NEVER update or delete rows in this table.
    Enforced at the DB level via the save() override below.
    """

    ACTION_CREATE   = "create"
    ACTION_EDIT     = "edit"
    ACTION_DELETE   = "delete"
    ACTION_LOGIN    = "login"
    ACTION_LOGOUT   = "logout"
    ACTION_ISSUE    = "coupon_issue"
    ACTION_REDEEM   = "coupon_redeem"
    ACTION_CANCEL   = "coupon_cancel"
    ACTION_CHOICES  = [
        (ACTION_CREATE,  "Create"),
        (ACTION_EDIT,    "Edit"),
        (ACTION_DELETE,  "Delete"),
        (ACTION_LOGIN,   "Login"),
        (ACTION_LOGOUT,  "Logout"),
        (ACTION_ISSUE,   "Coupon Issued"),
        (ACTION_REDEEM,  "Coupon Redeemed"),
        (ACTION_CANCEL,  "Coupon Cancelled"),
    ]

    # User may be null if account was deleted (preserved for audit integrity)
    user      = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL, null=True,
        related_name="audit_logs"
    )
    user_name = models.CharField(
        max_length=150,
        help_text="Snapshot of the user's name at time of action (preserved if user deleted)."
    )

    action    = models.CharField(max_length=20, choices=ACTION_CHOICES)
    module    = models.CharField(max_length=50, help_text="Which module/app the action occurred in.")
    record_id = models.CharField(
        max_length=50, blank=True,
        help_text="PK or identifier of the affected record."
    )
    detail    = models.TextField(
        blank=True,
        help_text="Human-readable description of what changed."
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table  = "audit_logs"
        ordering  = ["-timestamp"]
        # Database-level: no permissions to update/delete via Django ORM
        # Additional DB-level protection should be set via MySQL GRANT

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user_name} — {self.action} on {self.module}"

    def save(self, *args, **kwargs):
        # Prevent any update to an existing audit log entry
        if self.pk:
            raise PermissionError("AuditLog entries are immutable and cannot be modified.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError("AuditLog entries cannot be deleted.")
