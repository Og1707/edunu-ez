"""
Tests de servicios de autenticación — EduNúñez.

Verifica el comportamiento de crear_magic_link y verificar_magic_link
con el nuevo stack djangorestframework-simplejwt.
"""
from datetime import timedelta

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

from auth.models import MagicLinkToken
from auth.services import crear_magic_link, verificar_magic_link

User = get_user_model()


class MagicLinkServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="usuario_test",
            email="usuario@example.com",
            password="Password123!",
        )

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_crear_magic_link_envia_correo_y_crea_token(self):
        response = crear_magic_link(self.user.email)

        self.assertEqual(response["mensaje"], "Magic link enviado. Revisa tu correo.")
        self.assertEqual(MagicLinkToken.objects.filter(user=self.user).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_verificar_magic_link_retorna_simplejwt_tokens(self):
        """El payload de verificar_magic_link debe tener access y refresh (simplejwt)."""
        token_obj = MagicLinkToken.objects.create(user=self.user)

        result = verificar_magic_link(str(token_obj.token))

        self.assertIn("access", result)
        self.assertIn("refresh", result)
        self.assertEqual(result["email"], self.user.email)
        self.assertEqual(result["rol"], self.user.rol)

        # Verificar que el access token es decodificable por simplejwt
        decoded = AccessToken(result["access"])
        self.assertEqual(decoded["user_id"], self.user.id)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_verificar_magic_link_marca_token_como_usado(self):
        token_obj = MagicLinkToken.objects.create(user=self.user)
        verificar_magic_link(str(token_obj.token))

        token_obj.refresh_from_db()
        self.assertTrue(token_obj.used)

    def test_verificar_magic_link_expirado_lanza_error(self):
        token_obj = MagicLinkToken.objects.create(user=self.user)
        token_obj.created_at = timezone.now() - timedelta(minutes=16)
        token_obj.save(update_fields=["created_at"])

        with self.assertRaisesMessage(ValueError, "Token expirado"):
            verificar_magic_link(str(token_obj.token))

    def test_verificar_magic_link_ya_usado_lanza_error(self):
        token_obj = MagicLinkToken.objects.create(user=self.user, used=True)

        with self.assertRaisesMessage(ValueError, "El token ya fue usado"):
            verificar_magic_link(str(token_obj.token))

    def test_verificar_magic_link_invalido_lanza_error(self):
        with self.assertRaisesMessage(ValueError, "Token inválido"):
            verificar_magic_link("uuid-inexistente-0000-0000")

    def test_crear_magic_link_email_vacio_lanza_error(self):
        with self.assertRaisesMessage(ValueError, "El email es obligatorio"):
            crear_magic_link("")

    def test_crear_magic_link_email_no_registrado_lanza_error(self):
        with self.assertRaisesMessage(ValueError, "Email no registrado"):
            crear_magic_link("noexiste@example.com")
