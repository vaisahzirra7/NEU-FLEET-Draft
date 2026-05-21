"""
SMTP connection resolver.

Every email-sending site in the app should obtain its EmailBackend connection
through `get_mail_connection()` rather than going through django.core.mail's
default backend. This ensures:

  - If SystemSettings has SMTP overrides set, those are used.
  - If not, Django's settings.py-based config is used (backward compatibility).
  - A single source of truth — change Settings, restart NOT required.

Usage:
    from system_settings.mail import get_mail_connection
    conn = get_mail_connection()
    msg = EmailMultiAlternatives(..., connection=conn)
    msg.send()

The connection is cheap to construct (one TCP connection, opened lazily on
the first send call) so we don't try to cache it.
"""
import logging

logger = logging.getLogger(__name__)


def get_mail_connection(timeout=20):
    """
    Return a configured EmailBackend instance.

    Falls back to Django's default connection (django.core.mail.get_connection())
    if SystemSettings is unavailable for any reason — never let mail break
    because the DB is briefly unreachable.
    """
    from django.core.mail import get_connection

    try:
        from .models import SystemSettings
        s = SystemSettings.get()
        cfg = s.smtp_config()
    except Exception as e:
        logger.warning("Falling back to settings.py SMTP (DB unavailable: %s)", e)
        return get_connection()

    return get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=cfg["host"],
        port=cfg["port"],
        username=cfg["username"],
        password=cfg["password"],
        use_tls=cfg["use_tls"],
        use_ssl=cfg["use_ssl"],
        timeout=timeout,
    )


def test_smtp_config(host, port, username, password, use_tls, use_ssl,
                     from_addr, to_addr, timeout=10):
    """
    Try sending a tiny test email with the given config. Returns (ok, error_text).

    Used by the Settings page "Send Test Email" button before saving SMTP
    config — so admins discover broken creds BEFORE the next user creation
    fails silently.
    """
    import traceback
    from django.core.mail import EmailMessage, get_connection
    try:
        conn = get_connection(
            backend="django.core.mail.backends.smtp.EmailBackend",
            host=host, port=int(port),
            username=username, password=password,
            use_tls=bool(use_tls and not use_ssl),
            use_ssl=bool(use_ssl),
            timeout=timeout,
        )
        msg = EmailMessage(
            subject="VanaraFleetOps SMTP test",
            body=(
                "This is a test message sent from the System Settings page to "
                "verify your SMTP configuration. If you received this, your "
                "settings are valid."
            ),
            from_email=from_addr,
            to=[to_addr],
            connection=conn,
        )
        msg.send(fail_silently=False)
        return True, None
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        logger.warning("SMTP test failed: %s\n%s", err, traceback.format_exc())
        return False, err
