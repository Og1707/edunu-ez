"""
settings/production.py — Configuración para entorno de producción.

Activa con:
  DJANGO_SETTINGS_MODULE=edunuñez.settings.production

Variables de entorno OBLIGATORIAS en producción:
  DJANGO_SECRET_KEY        — clave secreta larga y aleatoria
  DATABASE_URL             — URL completa de conexión a PostgreSQL
  DJANGO_ALLOWED_HOSTS     — hosts permitidos separados por coma
  N8N_WEBHOOK_SECRET       — secret HMAC para validar webhooks entrantes

Variables RECOMENDADAS:
  SENTRY_DSN               — DSN de Sentry para captura de errores
  CLOUDINARY_CLOUD_NAME    — credenciales de Cloudinary
  CLOUDINARY_API_KEY
  CLOUDINARY_API_SECRET
"""
import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Validaciones obligatorias — falla rápido si la configuración es incorrecta
# ---------------------------------------------------------------------------


def _require_env(name: str) -> str:
    """Lanza ImproperlyConfigured si la variable de entorno está vacía."""
    value = os.environ.get(name, "")
    if not value:
        raise ImproperlyConfigured(
            f"La variable de entorno '{name}' es obligatoria en producción y no está configurada."
        )
    return value


SECRET_KEY = _require_env("DJANGO_SECRET_KEY")  # noqa: F405

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = False

ALLOWED_HOSTS = _require_env("DJANGO_ALLOWED_HOSTS").split(",")

# ---------------------------------------------------------------------------
# Seguridad HTTP
# ---------------------------------------------------------------------------
SECURE_HSTS_SECONDS = 31_536_000          # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# ---------------------------------------------------------------------------
# Cookies — solo vía HTTPS
# ---------------------------------------------------------------------------
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_HTTPONLY = False  # Necesario para que JS pueda leerlo
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True

# CSRF_TRUSTED_ORIGINS se configura vía variable de entorno en producción.
_csrf_origins = os.environ.get("DJANGO_CSRF_TRUSTED_ORIGINS", "")
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(",")]

# ---------------------------------------------------------------------------
# CORS — solo orígenes explícitos, nunca wildcard
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CORS_ALLOWED_ORIGINS", "https://edununez.com"
    ).split(",")
    if o.strip()
]

# ---------------------------------------------------------------------------
# Correo
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# ---------------------------------------------------------------------------
# drf-spectacular — /api/docs/ protegido en producción
# ---------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {  # noqa: F405
    **SPECTACULAR_SETTINGS,  # noqa: F405
    "SWAGGER_UI_SETTINGS": {
        "persistAuthorization": False,  # No persistir tokens en producción
    },
}

# ---------------------------------------------------------------------------
# Archivos estáticos — servidos por WhiteNoise o CDN
# ---------------------------------------------------------------------------
STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
