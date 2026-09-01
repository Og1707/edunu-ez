"""
settings/development.py — Configuración para entorno de desarrollo local.

Activa con:
  DJANGO_SETTINGS_MODULE=edunuñez.settings.development
  (este es el default en manage.py y pytest.ini)
"""
from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = True

if not SECRET_KEY:  # noqa: F405
    # Clave insegura solo para desarrollo; nunca llegar a producción con esto.
    SECRET_KEY = "django-insecure-dev-only-do-not-use-in-production-!@#"

ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# CORS — permisivo en desarrollo
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Correo — backend de consola para no enviar correos reales
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Cookies de sesión / CSRF — sin HTTPS en desarrollo
# ---------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = False

CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ---------------------------------------------------------------------------
# Django Extensions (opcional — instalar solo si está en requirements-dev)
# ---------------------------------------------------------------------------
try:
    import django_extensions  # noqa: F401
    INSTALLED_APPS += ["django_extensions"]  # noqa: F405
except ImportError:
    pass
