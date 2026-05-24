"""
Django settings for VanaraFleetOps.

Configuration is split between:
  - settings.py  → application code (apps, middleware, templates, URL conventions)
  - .env         → environment-specific values (secrets, DB credentials, hosts, debug flag)

If you're configuring a new deployment, you only need to fill in .env.
Copy .env.example → .env and edit the values.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from the project root. Must happen BEFORE any os.environ.get() calls below.
load_dotenv(BASE_DIR / ".env")


# ── Helpers ────────────────────────────────────────────────────────────────
def _env(key, default=None, required=False):
    """Read env var with optional default; raise if required and missing."""
    val = os.environ.get(key, default)
    if required and (val is None or val == ""):
        raise RuntimeError(
            f"Environment variable {key} is required. "
            f"Set it in .env or your hosting platform's environment config."
        )
    return val


def _env_bool(key, default=False):
    """Read env var as boolean. Accepts: 1/0, true/false, yes/no (case-insensitive)."""
    val = os.environ.get(key)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _env_list(key, default=None, sep=","):
    """Read env var as a comma-separated list."""
    val = os.environ.get(key)
    if not val:
        return default or []
    return [item.strip() for item in val.split(sep) if item.strip()]


# ── Core ───────────────────────────────────────────────────────────────────
SECRET_KEY = _env("SECRET_KEY", required=True)
DEBUG      = _env_bool("DEBUG", default=False)

# In DEBUG mode default to localhost-friendly hosts; in production require explicit list.
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS",
                          default=["localhost", "127.0.0.1"] if DEBUG else ["*"])

# New changes --- Added "*" to ALLOWED_HOSTS for production, to go back remove the "*".


# ── Applications ───────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # Project apps
    "accounts",
    "vehicles",
    "generators",
    "drivers",
    "vendors",
    "coupons",
    "fuel_logs",
    "maintenance",
    "reports",
    "audit",
    "trips",
    "system_settings",
    "station_deposits",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "accounts.middleware.LoginRequiredMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF     = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "system_settings.context_processors.branding",
            ],
        },
    },
]


# ── Database ───────────────────────────────────────────────────────────────
# Default engine is mysql to match current dev setup; override DB_ENGINE in
# .env if deploying to Postgres (e.g. on Render: django.db.backends.postgresql).
DATABASES = {
    "default": {
        "ENGINE":   _env("DB_ENGINE",   "django.db.backends.mysql"),
        "NAME":     _env("DB_NAME",     required=True),
        "USER":     _env("DB_USER",     required=True),
        "PASSWORD": _env("DB_PASSWORD", default=""),
        "HOST":     _env("DB_HOST",     "localhost"),
        "PORT":     _env("DB_PORT",     "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            "ssl": {"ssl-mode": "REQUIRED"},
        } if _env("DB_ENGINE", "django.db.backends.mysql").endswith("mysql") else {},
    }
}


# ── Auth ───────────────────────────────────────────────────────────────────
AUTH_USER_MODEL     = "accounts.User"
LOGIN_URL           = "/auth/login/"
LOGIN_REDIRECT_URL  = "/dashboard/"
LOGOUT_REDIRECT_URL = "/auth/login/"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ── Internationalisation ───────────────────────────────────────────────────
LANGUAGE_CODE = "en-gb"
TIME_ZONE     = "Africa/Lagos"
USE_I18N      = True
USE_TZ        = True


# ── Static / Media ─────────────────────────────────────────────────────────
STATIC_URL       = "/static/"
STATIC_ROOT      = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL        = "/media/"
MEDIA_ROOT       = BASE_DIR / "media"


# ── System settings encryption ─────────────────────────────────────────────
# Used to encrypt SMTP password (and any future secrets) stored in the
# system_settings DB row. If not set, falls back to a SECRET_KEY-derived key —
# weaker, because rotating SECRET_KEY would invalidate stored secrets.
SETTINGS_ENCRYPTION_KEY = _env("SETTINGS_ENCRYPTION_KEY", default=None)


# ── Default PK ─────────────────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ── Report Logo (fallback if SystemSettings.logo is not set) ───────────────
REPORT_LOGO_PATH = BASE_DIR / "static" / "images" / "neu_logo.png"
REPORT_LOGO_URL  = "/static/images/neu_logo.png"


# ── Email ──────────────────────────────────────────────────────────────────
# These are the fallback values used when SystemSettings.smtp_overrides_active
# is False. Once an admin configures SMTP via /settings/, the DB values take
# precedence (see system_settings.mail.get_mail_connection).
EMAIL_BACKEND       = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST          = _env("EMAIL_HOST",          "smtp.zoho.com")
EMAIL_PORT          = int(_env("EMAIL_PORT",      "587"))
EMAIL_USE_TLS       = _env_bool("EMAIL_USE_TLS",  default=True)
EMAIL_USE_SSL       = _env_bool("EMAIL_USE_SSL",  default=False)
EMAIL_HOST_USER     = _env("EMAIL_HOST_USER",     default="")
EMAIL_HOST_PASSWORD = _env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL  = _env("DEFAULT_FROM_EMAIL",  default=EMAIL_HOST_USER or "noreply@example.com")


# ── Session ────────────────────────────────────────────────────────────────
SESSION_COOKIE_AGE              = int(_env("SESSION_COOKIE_AGE", "28800"))  # 8 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
