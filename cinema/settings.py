import sys
from pathlib import Path
from apps.common.jwt_config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    JWT_ACCESS_TOKEN_LIFETIME,
    JWT_REFRESH_TOKEN_LIFETIME,
)

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "apps"))


SECRET_KEY = "django-insecure-4+z1414a*e3)(4!(l=u*qf8dp0pb#gzp^tzh-fn0#px%%)*bkn"


DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "apps.movies",
    "apps.users",
    "apps.schedule",
    "apps.common",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cinema.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "cinema.wsgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "cinema_db",
        "USER": "cinema",
        "PASSWORD": "Barsik_04",
        "HOST": "localhost",
        "PORT": "5432",
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


LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Asia/Almaty"

USE_I18N = True

USE_TZ = True


STATIC_URL = "static/"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# user
AUTH_USER_MODEL = "users.User"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
}

# jwt
SIMPLE_JWT = {
    "SIGNING_KEY": JWT_SECRET_KEY,
    "ALGORITHM": JWT_ALGORITHM,
    "ACCESS_TOKEN_LIFETIME": JWT_ACCESS_TOKEN_LIFETIME,
    "REFRESH_TOKEN_LIFETIME": JWT_REFRESH_TOKEN_LIFETIME,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
