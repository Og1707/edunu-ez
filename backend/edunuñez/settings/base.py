"""
settings/base.py — Configuración base compartida entre todos los ambientes.

NO incluye configuraciones que difieran entre desarrollo y producción.
Esas van en development.py y production.py respectivamente.
"""
import os
import sys
import urllib.parse
from datetime import timedelta
from pathlib import Path

import cloudinary

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
# BASE_DIR apunta a backend/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

try:
    from dotenv import load_dotenv

    # Buscar .env primero en backend/, luego en la raíz del repo.
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        env_path = BASE_DIR.parent / ".env"
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Seguridad
# ---------------------------------------------------------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "")
# La validación de SECRET_KEY no-vacío se hace en production.py.

# ---------------------------------------------------------------------------
# Aplicaciones
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Terceros
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "axes",
    "drf_spectacular",
    # Dominio
    "apps.core",
    "apps.usuarios",
    "apps.cursos",
    "apps.actividades",
    "apps.plantillas",
    "apps.juegos",
    "apps.ciencias",
    "apps.integraciones",
    "auth",
    "api",
]

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "api.middleware.RequestLoggingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "axes.middleware.AxesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "edunuñez.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR.parent / "frontend" / "build")],
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

WSGI_APPLICATION = "edunuñez.wsgi.application"

# ---------------------------------------------------------------------------
# Base de datos
# ---------------------------------------------------------------------------
DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("DJANGO_DATABASE_URL")

if DATABASE_URL:
    _url = urllib.parse.urlparse(DATABASE_URL)
    _db_host = _url.hostname or "127.0.0.1"
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _url.path.lstrip("/") if _url.path else "postgres",
            "USER": _url.username or "postgres",
            "PASSWORD": _url.password or "",
            "HOST": _db_host,
            "PORT": str(_url.port or 5432),
            "OPTIONS": (
                {"sslmode": "require"}
                if _db_host not in ("localhost", "127.0.0.1", "db")
                else {}
            ),
        }
    }
else:
    _db_host = (
        os.environ.get("DJANGO_DB_HOST")
        or os.environ.get("DB_HOST", "127.0.0.1")
    )
    DATABASES = {
        "default": {
            "ENGINE": (
                os.environ.get("DJANGO_DB_ENGINE")
                or os.environ.get("DB_ENGINE", "django.db.backends.postgresql")
            ),
            "NAME": (
                os.environ.get("DJANGO_DB_NAME")
                or os.environ.get("DB_NAME", "edununez")
            ),
            "USER": (
                os.environ.get("DJANGO_DB_USER")
                or os.environ.get("DB_USER", "postgres")
            ),
            "PASSWORD": (
                os.environ.get("DJANGO_DB_PASSWORD")
                or os.environ.get("DB_PASSWORD", "postgres")
            ),
            "HOST": _db_host,
            "PORT": (
                os.environ.get("DJANGO_DB_PORT")
                or os.environ.get("DB_PORT", "5432")
            ),
            "OPTIONS": (
                {"sslmode": "require"}
                if _db_host not in ("localhost", "127.0.0.1", "db")
                else {}
            ),
        }
    }

# SQLite en memoria para pytest (sobreescribible con USE_POSTGRES_TESTS=true)
_is_test = any("pytest" in arg for arg in sys.argv) or "test" in sys.argv
if _is_test and os.environ.get("USE_POSTGRES_TESTS", "false").lower() not in ("true", "1"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }

# ---------------------------------------------------------------------------
# Caché — Redis
# ---------------------------------------------------------------------------
REDIS_URL = os.environ.get("DJANGO_REDIS_URL", "redis://127.0.0.1:6379/1")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}
# Tests usan caché en memoria para evitar depender de Redis.
if _is_test:
    CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }

# ---------------------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------------------
AUTH_USER_MODEL = "usuarios.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ---------------------------------------------------------------------------
# djangorestframework-simplejwt
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "EXCEPTION_HANDLER": "api.utils.exception_handler.custom_exception_handler",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
        "rest_framework.throttling.AnonRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "auth": "15/min",
        "actividades_completar": "30/min",
        "invitaciones": "10/hour",
        "anon": "100/day",
        "user": "1000/day",
    },
    "DEFAULT_THROTTLE_CACHE": "default",
}

# ---------------------------------------------------------------------------
# drf-spectacular (OpenAPI)
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "EduNúñez API",
    "DESCRIPTION": (
        "Plataforma educativa de ciencias naturales. "
        "Gestión de actividades, cursos, juegos y reportes pedagógicos."
    ),
    "VERSION": "2.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/",
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": True,
        "displayRequestDuration": True,
    },
}

# ---------------------------------------------------------------------------
# Axes (protección brute-force)
# ---------------------------------------------------------------------------
AXES_ENABLED = True
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=15)
AXES_LOCKOUT_PARAMETERS = ["ip_address"]
AXES_CACHE = "default"
AXES_LOCK_OUT_AT_FAILURE = True

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-request-id",
    "x-n8n-signature",
]

# ---------------------------------------------------------------------------
# Correo electrónico
# ---------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = os.environ.get(
    "DJANGO_DEFAULT_FROM_EMAIL", "no-reply@edununez.local"
)
EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.environ.get("DJANGO_EMAIL_USE_TLS", "True").lower() in ("true", "1")
EMAIL_USE_SSL = os.environ.get("DJANGO_EMAIL_USE_SSL", "False").lower() in ("true", "1")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:3000")

# ---------------------------------------------------------------------------
# Cloudinary
# ---------------------------------------------------------------------------
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.environ.get("CLOUDINARY_API_KEY", ""),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET", ""),
)
CLOUDINARY_MAX_FILE_SIZE = int(os.environ.get("CLOUDINARY_MAX_FILE_SIZE", 104_857_600))
CLOUDINARY_ALLOWED_VIDEO_FORMATS = ["mp4", "avi", "mov", "flv", "wmv", "webm", "mkv"]
CLOUDINARY_ALLOWED_AUDIO_FORMATS = ["mp3", "wav", "aac", "flac", "ogg", "m4a"]
CLOUDINARY_ALLOWED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"]

# ---------------------------------------------------------------------------
# Integración n8n / Webhooks
# ---------------------------------------------------------------------------
N8N_WEBHOOK_URL = os.environ.get(
    "N8N_WEBHOOK_URL", "http://localhost:5678/webhook/Alumnos_settings"
)
N8N_WEBHOOK_ENABLED = os.environ.get("N8N_WEBHOOK_ENABLED", "True").lower() in (
    "true", "1",
)
N8N_WEBHOOK_TIMEOUT = int(os.environ.get("N8N_WEBHOOK_TIMEOUT", "10"))
N8N_WEBHOOK_RETRY_ATTEMPTS = int(os.environ.get("N8N_WEBHOOK_RETRY_ATTEMPTS", "3"))
# Secret HMAC para validar la firma de los webhooks entrantes de n8n.
# OBLIGATORIO en producción — genera con: python -c "import secrets; print(secrets.token_hex(32))"
N8N_WEBHOOK_SECRET = os.environ.get("N8N_WEBHOOK_SECRET", "")

# ---------------------------------------------------------------------------
# Sentry — Monitoreo de errores en producción
# ---------------------------------------------------------------------------
_sentry_dsn = os.environ.get("SENTRY_DSN", "")
if _sentry_dsn:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=_sentry_dsn,
        integrations=[
            DjangoIntegration(transaction_style="url"),
            LoggingIntegration(level=None, event_level="ERROR"),
        ],
        traces_sample_rate=float(os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        environment=os.environ.get("DJANGO_ENV", "development"),
        # No enviar datos del usuario por defecto (GDPR).
        send_default_pii=False,
    )

# ---------------------------------------------------------------------------
# Logging estructurado JSON
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": (
                "%(asctime)s %(levelname)s %(name)s %(message)s "
                "%(request_id)s %(user_id)s %(duration_ms)s"
            ),
        },
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            # En tests usa el formatter verboso para que sea legible.
            "formatter": "verbose" if _is_test else "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "INFO"),
    },
    "loggers": {
        "django": {"handlers": ["console"], "level": "WARNING", "propagate": False},
        "api": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "auth": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

# ---------------------------------------------------------------------------
# Archivos estáticos
# ---------------------------------------------------------------------------
STATIC_URL = "static/"
_frontend_static = BASE_DIR.parent / "frontend" / "build" / "static"
STATICFILES_DIRS = [str(_frontend_static)] if _frontend_static.exists() else []

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
