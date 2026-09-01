"""
Tests de integración para autenticación y webhooks — EduNúñez.

Cubre:
  - Magic link happy path (access + refresh en respuesta)
  - Token expirado → 400
  - Rate limit invitaciones → 429
  - IDOR invitaciones → 403
  - Webhook sin firma → 403
  - Webhook con firma inválida → 403
  - Webhook con firma válida → flujo normal
"""
import hashlib
import hmac
import json
from datetime import timedelta

from django.conf import settings
from django.test import override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from auth.models import Invitation, MagicLinkToken

User = get_user_model()


class MagicLinkIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="usuario2",
            email="usuario2@example.com",
            password="Password123!",
        )
        self.client = APIClient()

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_magic_link_happy_path_retorna_access_y_refresh(self):
        """El flujo completo de magic link debe retornar access y refresh."""
        response = self.client.post(
            "/auth/magic-link/", {"email": self.user.email}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token_obj = MagicLinkToken.objects.get(user=self.user)
        verify = self.client.get(f"/auth/magic-link/verify/?token={token_obj.token}")

        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        self.assertIn("access", verify.data)
        self.assertIn("refresh", verify.data)
        # Verificar que los datos del usuario están presentes
        self.assertEqual(verify.data["email"], self.user.email)

    def test_magic_link_token_expirado_retorna_400(self):
        token_obj = MagicLinkToken.objects.create(user=self.user)
        token_obj.created_at = timezone.now() - timedelta(minutes=16)
        token_obj.save(update_fields=["created_at"])

        response = self.client.get(f"/auth/magic-link/verify/?token={token_obj.token}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Token expirado")

    def test_invitacion_rate_limit_por_usuario(self):
        self.client.force_authenticate(user=self.user)
        for index in range(9):
            payload = {"email": f"invitado{index}@example.com"}
            resp = self.client.post("/auth/invitaciones/", payload, format="json")
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        resp = self.client.post(
            "/auth/invitaciones/", {"email": "limite@example.com"}, format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(resp.data["detail"], "Límite de invitaciones alcanzado. Intenta en 1 hora.")

    def test_invitacion_idor_retorna_403(self):
        owner = User.objects.create_user(
            username="dueno",
            email="dueno@example.com",
            password="Password123!",
        )
        invitation = Invitation.objects.create(
            created_by=owner, email="victima@example.com"
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/auth/invitaciones/{invitation.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WebhookHMACTests(APITestCase):
    """Tests de seguridad del endpoint receptor de webhooks de n8n."""

    WEBHOOK_URL = "/api/webhooks/n8n/"
    SECRET = "test-secret-key-32-chars-minimum!!"

    def _firma_valida(self, body: bytes) -> str:
        digest = hmac.new(
            key=self.SECRET.encode("utf-8"),
            msg=body,
            digestmod=hashlib.sha256,
        ).hexdigest()
        return f"sha256={digest}"

    @override_settings(N8N_WEBHOOK_SECRET="")
    def test_webhook_sin_secret_configurado_retorna_403(self):
        """Sin N8N_WEBHOOK_SECRET configurado el webhook debe ser rechazado."""
        response = self.client.post(
            self.WEBHOOK_URL,
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(N8N_WEBHOOK_SECRET=SECRET)
    def test_webhook_sin_header_firma_retorna_403(self):
        """Un POST sin el header X-N8N-Signature debe ser rechazado."""
        response = self.client.post(
            self.WEBHOOK_URL,
            data=json.dumps({"test": "data"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(N8N_WEBHOOK_SECRET=SECRET)
    def test_webhook_con_firma_invalida_retorna_403(self):
        """Una firma incorrecta debe ser rechazada."""
        response = self.client.post(
            self.WEBHOOK_URL,
            data=json.dumps({"test": "data"}),
            content_type="application/json",
            HTTP_X_N8N_SIGNATURE="sha256=firmainvalida0000",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @override_settings(N8N_WEBHOOK_SECRET=SECRET)
    def test_webhook_con_firma_valida_pasa_validacion(self):
        """Una firma HMAC válida debe pasar la validación (puede fallar por datos del serializer)."""
        body = json.dumps({"test": "data"}).encode("utf-8")
        firma = self._firma_valida(body)

        response = self.client.post(
            self.WEBHOOK_URL,
            data=body,
            content_type="application/json",
            HTTP_X_N8N_SIGNATURE=firma,
        )
        # No debe ser 403 (la firma fue aceptada)
        # Puede ser 400 si el serializer rechaza los datos de prueba, eso es correcto.
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)
