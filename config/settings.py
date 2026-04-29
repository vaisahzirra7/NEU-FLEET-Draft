from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-CHANGE-THIS-IN-PRODUCTION-USE-ENV-VAR'

DEBUG = True

ALLOWED_HOSTS = ['*']

# ── Applications ───────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Project apps — one per module
    'accounts',
    'vehicles',
    'drivers',
    'vendors',
    'coupons',
    'fuel_logs',
    'maintenance',
    'reports',
    'audit',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',       # static files in production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accounts.middleware.LoginRequiredMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # global templates folder
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ── Database ───────────────────────────────────────────────────
# Switch to MySQL for production. For local dev you can use SQLite
# by swapping the ENGINE line.
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     'vanara_fleets',         # create this DB in MySQL first
        'USER':     'root',                  # change to your MySQL user
        'PASSWORD': 'I.VaNara@070305',                      # set your MySQL password
        'HOST':     'localhost',
        'PORT':     '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# ── Auth ───────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'

# Where to redirect after login / logout
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/auth/login/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
     'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalisation ───────────────────────────────────────
LANGUAGE_CODE = 'en-gb'
TIME_ZONE     = 'Africa/Lagos'      # Nigerian time (GMT+1)
USE_I18N      = True
USE_TZ        = True

# ── Static / Media ─────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Default PK ────────────────────────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Email (optional — configure when SMTP details are available) ──
EMAIL_BACKEND       = 'django.core.mail.backends.console.EmailBackend'  # dev mode
# EMAIL_BACKEND     = 'django.core.mail.backends.smtp.EmailBackend'     # production
# EMAIL_HOST        = 'smtp.youruniversity.edu.ng'
# EMAIL_PORT        = 587
# EMAIL_USE_TLS     = True
# EMAIL_HOST_USER   = 'fleet@youruniversity.edu.ng'
# EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')

# ── Session ────────────────────────────────────────────────────
SESSION_COOKIE_AGE     = 28800   # 8 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
