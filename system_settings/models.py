from django.db import models


def _logo_path(instance, filename):
    """Always overwrite to the same name so the URL stays stable across edits."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "png"
    return f"branding/logo.{ext}"


def _favicon_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "ico"
    return f"branding/favicon.{ext}"


class SystemSettings(models.Model):
    """
    Singleton model for system-wide branding and configuration.

    There is always exactly ONE row in this table; the migration seeds it,
    and SystemSettings.get() always returns that row (creating it if a fresh
    deploy somehow ended up without one).

    Anything an institution might reasonably want to change without touching
    code goes here. Currently: brand text, logo, favicon, email-from address.
    Things that are NOT here (and stay in Django settings) are operational
    config: SMTP host, secret key, DB credentials.
    """

    SYSTEM_NAME_DEFAULT  = "VanaraFleetsOps"
    INST_NAME_DEFAULT    = "VanaraFleetsOps"
    INST_SUBTITLE_DEFAULT= "North-Eastern University, Gombe  ·  FMS"
    EMAIL_FROM_DEFAULT   = "fleet@neu.edu.ng"

    system_name = models.CharField(
        max_length=120, default=SYSTEM_NAME_DEFAULT,
        help_text="Internal product name. Used in browser tab titles and email subjects."
    )
    institution_name = models.CharField(
        max_length=160, default=INST_NAME_DEFAULT,
        help_text="Big text shown next to the logo in the sidebar (e.g. 'VanaraFleetsOps')."
    )
    institution_subtitle = models.CharField(
        max_length=200, blank=True, default=INST_SUBTITLE_DEFAULT,
        help_text="Smaller line under the institution name (e.g. 'University of X · FMS')."
    )
    logo = models.ImageField(
        upload_to=_logo_path, blank=True, null=True,
        help_text="Square or near-square logo for the sidebar. PNG/JPG/SVG. ~120x120 recommended."
    )
    favicon = models.ImageField(
        upload_to=_favicon_path, blank=True, null=True,
        help_text="Small icon shown in the browser tab. PNG or ICO. 32x32 or 64x64 recommended."
    )
    email_from = models.EmailField(
        max_length=200, default=EMAIL_FROM_DEFAULT,
        help_text="From-address used for scheduled report emails and password resets."
    )

    # ── SMTP configuration (overrides settings.py when filled) ──
    # When ALL of these are blank/null, the system falls back to Django settings.
    # When ANY is set, the active config is read from the DB for outbound mail.
    smtp_host = models.CharField(
        max_length=200, blank=True, default="",
        help_text="SMTP server hostname (e.g. smtp.zoho.com). Leave blank to use settings.py."
    )
    smtp_port = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="SMTP server port. Typical: 587 (TLS), 465 (SSL), 25 (legacy)."
    )
    smtp_user = models.CharField(
        max_length=200, blank=True, default="",
        help_text="SMTP login username (usually an email address)."
    )
    smtp_password_encrypted = models.TextField(
        blank=True, default="",
        help_text="SMTP password stored encrypted. NEVER displayed in the UI."
    )
    smtp_use_tls = models.BooleanField(
        default=True,
        help_text="Use STARTTLS (port 587). Mutually exclusive with SSL."
    )
    smtp_use_ssl = models.BooleanField(
        default=False,
        help_text="Use direct SSL/TLS on connect (port 465). Mutually exclusive with TLS."
    )

    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        "accounts.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="+",
    )

    class Meta:
        db_table = "system_settings"
        verbose_name = "System Settings"
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.institution_name or "System Settings"

    @classmethod
    def get(cls):
        """Singleton accessor. Always returns the one settings row."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def logo_url(self):
        """Safe accessor: returns URL or None."""
        try:
            return self.logo.url if self.logo and self.logo.name else None
        except (ValueError, FileNotFoundError):
            return None

    @property
    def favicon_url(self):
        try:
            return self.favicon.url if self.favicon and self.favicon.name else None
        except (ValueError, FileNotFoundError):
            return None

    # ── SMTP helpers ────────────────────────────────────────────────────────
    @property
    def smtp_overrides_active(self):
        """
        True if the SMTP fields are populated enough to override settings.py.
        Used by mail helpers to decide which config to use.
        """
        return bool(self.smtp_host and self.smtp_port and self.smtp_user
                    and self.smtp_password_encrypted)

    def set_smtp_password(self, plain):
        """Encrypt and store SMTP password. Pass empty string to clear."""
        from .encryption import encrypt
        self.smtp_password_encrypted = encrypt(plain) if plain else ""

    def get_smtp_password(self):
        """Decrypt and return the SMTP password (empty if none set)."""
        from .encryption import decrypt
        return decrypt(self.smtp_password_encrypted)

    def smtp_config(self):
        """
        Returns the active SMTP config as a dict suitable for
        django.core.mail.backends.smtp.EmailBackend(...) kwargs.

        Falls back to Django settings when DB overrides are not active.
        Reason: never let an empty DB row break outbound mail entirely.
        """
        from django.conf import settings
        if self.smtp_overrides_active:
            return {
                "host":     self.smtp_host,
                "port":     self.smtp_port,
                "username": self.smtp_user,
                "password": self.get_smtp_password(),
                "use_tls":  bool(self.smtp_use_tls and not self.smtp_use_ssl),
                "use_ssl":  bool(self.smtp_use_ssl),
            }
        return {
            "host":     getattr(settings, "EMAIL_HOST", ""),
            "port":     getattr(settings, "EMAIL_PORT", 587),
            "username": getattr(settings, "EMAIL_HOST_USER", ""),
            "password": getattr(settings, "EMAIL_HOST_PASSWORD", ""),
            "use_tls":  getattr(settings, "EMAIL_USE_TLS", True),
            "use_ssl":  getattr(settings, "EMAIL_USE_SSL", False),
        }
