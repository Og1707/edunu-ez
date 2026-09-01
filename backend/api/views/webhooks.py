"""
Vista receptora de webhooks enviados desde n8n — EduNúñez.

Seguridad:
  - Valida la firma HMAC-SHA256 del cuerpo del request usando el secret
    compartido N8N_WEBHOOK_SECRET definido en settings/variables de entorno.
  - Si la firma es inválida o falta el header, responde 403 inmediatamente.
  - La comparación usa hmac.compare_digest para prevenir timing attacks.

Header esperado:
  X-N8N-Signature: sha256=<hex_digest>
"""
import hashlib
import hmac
import json
import logging

from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse, inline_serializer
from rest_framework import serializers as drf_serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import PartidaJuegoWebhookSerializer

logger = logging.getLogger(__name__)


def _verificar_firma_hmac(body: bytes, signature_header: str | None) -> bool:
    """
    Verifica que el header X-N8N-Signature coincide con HMAC-SHA256 del body.

    Formato esperado del header: "sha256=<hex_digest>"

    Returns:
        True si la firma es válida, False en caso contrario.
    """
    secret = getattr(settings, "N8N_WEBHOOK_SECRET", "")
    if not secret:
        # Si no hay secret configurado, rechazar siempre para no operar inseguro.
        logger.error(
            "N8N_WEBHOOK_SECRET no está configurado. Webhook rechazado.",
            extra={"event": "webhook_no_secret"},
        )
        return False

    if not signature_header:
        return False

    # El header tiene formato "sha256=<digest>", extraemos solo el digest.
    parts = signature_header.split("=", 1)
    if len(parts) != 2 or parts[0] != "sha256":
        return False

    expected_digest = parts[1]
    computed_digest = hmac.new(
        key=secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Comparación en tiempo constante para prevenir timing attacks.
    return hmac.compare_digest(computed_digest, expected_digest)


class RecipientWebhooks(APIView):
    """
    Receptor de webhooks de n8n.

    POST /api/webhooks/n8n/
    Headers:
        X-N8N-Signature: sha256=<hmac_sha256_del_body>
    Body: JSON con datos de la partida de juego.
    """

    # Sin autenticación de sesión/JWT, la seguridad la da la firma HMAC.
    authentication_classes = []
    permission_classes = []

    @extend_schema(
        tags=["Webhooks"],
        summary="Receptor de webhooks de n8n",
        description=(
            "Recibe notificaciones de n8n sobre resultados de actividades. "
            "Requiere el header `X-N8N-Signature: sha256=<hmac>` para autenticación HMAC."
        ),
        request=PartidaJuegoWebhookSerializer,
        responses={
            201: inline_serializer(
                name="WebhookSuccess",
                fields={"mensaje": drf_serializers.CharField()},
            ),
            400: OpenApiResponse(description="Datos inválidos"),
            403: OpenApiResponse(description="Firma HMAC inválida o ausente"),
        },
    )
    def post(self, request, *args, **kwargs):
        # --- Validación de firma HMAC ---
        raw_body = request.body  # bytes crudos antes de parsear
        signature = request.headers.get("X-N8N-Signature")

        if not _verificar_firma_hmac(raw_body, signature):
            logger.warning(
                "Webhook rechazado: firma HMAC inválida o ausente.",
                extra={
                    "event": "webhook_invalid_signature",
                    "ip": request.META.get("REMOTE_ADDR"),
                    "signature_header": signature,
                },
            )
            return Response(
                {"error": "Firma inválida o ausente."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # --- Parseo seguro del body ---
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            logger.warning(
                "Webhook rechazado: body no es JSON válido.",
                extra={"event": "webhook_bad_json", "error": str(exc)},
            )
            return Response(
                {"error": "El body debe ser JSON válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.info(
            "Webhook de n8n recibido y firma validada.",
            extra={"event": "webhook_received", "keys": list(payload.keys())},
        )

        # --- Persistencia ---
        serializer = PartidaJuegoWebhookSerializer(data=payload)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"mensaje": "Webhook recibido y partida guardada exitosamente."},
                status=status.HTTP_201_CREATED,
            )

        logger.error(
            "Webhook rechazado: datos inválidos según el serializer.",
            extra={"event": "webhook_validation_error", "errors": serializer.errors},
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
