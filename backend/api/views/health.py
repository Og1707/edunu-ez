"""
Vista de health check — EduNúñez.

GET /api/health/
  Responde con el estado del servicio, la base de datos y Redis.
  Usada por el healthcheck de Docker y por sistemas de monitoreo externos.

  Response 200: { "status": "ok", "db": true, "redis": true, "version": "2.0.0" }
  Response 503: { "status": "degraded", "db": false, "redis": false, "errors": [...] }

No requiere autenticación — es pública intencionalmente para que los load
balancers puedan sondearla sin credenciales.
"""
import logging

from django.db import connection, OperationalError as DbOperationalError
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiResponse
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

logger = logging.getLogger(__name__)

_VERSION = "2.0.0"


def _check_db() -> tuple[bool, str | None]:
    """Verifica que la base de datos responde. Retorna (ok, error_msg)."""
    try:
        connection.ensure_connection()
        return True, None
    except DbOperationalError as exc:
        return False, str(exc)


def _check_redis() -> tuple[bool, str | None]:
    """Verifica que Redis responde. Retorna (ok, error_msg)."""
    try:
        cache.set("__health_check__", "1", timeout=5)
        val = cache.get("__health_check__")
        return val == "1", None
    except Exception as exc:  # redis.exceptions.ConnectionError etc.
        return False, str(exc)


@extend_schema(
    tags=["Infraestructura"],
    summary="Health check del servicio",
    description=(
        "Verifica el estado de la aplicación, la base de datos y Redis. "
        "Usada por Docker healthcheck y sistemas de monitoreo externos. "
        "No requiere autenticación."
    ),
    responses={
        200: inline_serializer(
            name="HealthOk",
            fields={
                "status": drf_serializers.ChoiceField(choices=["ok", "degraded"]),
                "version": drf_serializers.CharField(),
                "db": drf_serializers.BooleanField(),
                "redis": drf_serializers.BooleanField(),
            },
        ),
        503: OpenApiResponse(description="Uno o más servicios no disponibles"),
    },
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def health_check(request):
    """
    Endpoint de salud del servicio.

    Verifica conectividad con PostgreSQL y Redis.
    Retorna 200 si ambos están ok, 503 si alguno falla.
    """
    db_ok, db_error = _check_db()
    redis_ok, redis_error = _check_redis()

    errors = []
    if not db_ok:
        errors.append(f"db: {db_error}")
        logger.error("Health check: DB no disponible. %s", db_error)
    if not redis_ok:
        errors.append(f"redis: {redis_error}")
        logger.error("Health check: Redis no disponible. %s", redis_error)

    all_ok = db_ok and redis_ok
    payload = {
        "status": "ok" if all_ok else "degraded",
        "version": _VERSION,
        "db": db_ok,
        "redis": redis_ok,
    }
    if errors:
        payload["errors"] = errors

    http_status = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(payload, status=http_status)
