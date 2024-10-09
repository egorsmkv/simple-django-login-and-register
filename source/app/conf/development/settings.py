import warnings
from pathlib import Path

from django.utils.translation import gettext_lazy as _

warnings.simplefilter("error", DeprecationWarning)

BASE_DIR = Path(__file__).resolve().parents[3]
CONTENT_DIR = BASE_DIR / "content"

SECRET_KEY = "NhfTvayqggTBPswCXXhWaN69HuglgZIkM"

DEBUG = True
ALLOWED_HOSTS = ["*"]

SITE_ID = 1

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Vendor apps
    "bootstrap4",
    # Application apps
    "main",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "app.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            CONTENT_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = CONTENT_DIR / "tmp" / "emails"
EMAIL_HOST_USER = "test@example.com"
DEFAULT_FROM_EMAIL = "test@example.com"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

ENABLE_USER_ACTIVATION = True
DISABLE_USERNAME = False
LOGIN_VIA_EMAIL = True
LOGIN_VIA_EMAIL_OR_USERNAME = False
LOGIN_REDIRECT_URL = "index"
LOGIN_URL = "accounts:log_in"
USE_REMEMBER_ME = True

RESTORE_PASSWORD_VIA_EMAIL_OR_USERNAME = False
ENABLE_ACTIVATION_AFTER_EMAIL_CHANGE = True

SIGN_UP_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "email",
    "password1",
    "password2",
]
if DISABLE_USERNAME:
    SIGN_UP_FIELDS = ["first_name", "last_name", "email", "password1", "password2"]

MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"

USE_I18N = True
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", _("English")),
    ("zh-Hans", _("Simplified Chinese")),
    ("fr", _("French")),
    ("es", _("Spanish")),
]

TIME_ZONE = "UTC"
USE_TZ = True

STATIC_ROOT = CONTENT_DIR / "static"
STATIC_URL = "/static/"

MEDIA_ROOT = CONTENT_DIR / "media"
MEDIA_URL = "/media/"

STATICFILES_DIRS = [
    CONTENT_DIR / "assets",
]

LOCALE_PATHS = [CONTENT_DIR / "locale"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
