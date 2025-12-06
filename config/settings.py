from pathlib import Path
import os
from dotenv import load_dotenv

# -----------------------
# BASE DIRECTORY
# -----------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------
# ENV CONFIG
# -----------------------
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-dev-key")

DEBUG = os.getenv("DEBUG", "False") == "True"

# -----------------------
# ALLOWED HOSTS (RENDER FIX)
# -----------------------

# Always start safe
# ----------------------
# ALLOWED HOSTS (production safe)
# ----------------------

env_hosts = os.getenv("ALLOWED_HOSTS")

if env_hosts and env_hosts.strip():
    ALLOWED_HOSTS = [h.strip() for h in env_hosts.split(",") if h.strip()]
else:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Absolute fallback (prevents broken deploys)
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

# -----------------------
# APPLICATIONS
# -----------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",

    "accounts",
    "travel",
    "expenses",
    "policies",
]


# -----------------------
# MIDDLEWARE
# -----------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# -----------------------
# URL ROUTING
# -----------------------

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# -----------------------
# DATABASE
# -----------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# -----------------------
# PASSWORD VALIDATION
# -----------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# -----------------------
# INTERNATIONALIZATION
# -----------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# -----------------------
# STATIC FILES
# -----------------------

STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -----------------------
# DJANGO REST FRAMEWORK
# -----------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
