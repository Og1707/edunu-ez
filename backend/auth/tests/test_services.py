import jwt
from datetime import timedelta
from django.conf import settings
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model

from auth.models import MagicLinkToken
from auth.services import crear_magic_link, verificar_magic_link


User = get_user_model()


class MagicLinkServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario',
            email='usuario@example.com',
            password='Password123!'
        )

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_crear_magic_link_envia_correo_y_crea_token(self):
        response = crear_magic_link(self.user.email)
        self.assertEqual(response['mensaje'], 'Magic link enviado. Revisa tu correo.')
        self.assertEqual(MagicLinkToken.objects.filter(user=self.user).count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_verificar_magic_link_retornara_jwt_y_marcar_token_usado(self):
        token_obj = MagicLinkToken.objects.create(user=self.user)
        result = verificar_magic_link(str(token_obj.token))
        self.assertTrue('access' in result)
        token_obj.refresh_from_db()
        self.assertTrue(token_obj.used)
        jwt_str = result['access']['token']
        payload = jwt.decode(jwt_str, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        self.assertEqual(payload['user_id'], self.user.id)

    def test_verificar_magic_link_expirado_lanza_error(self):
        token_obj = MagicLinkToken.objects.create(user=self.user)
        token_obj.created_at = timezone.now() - timedelta(minutes=16)
        token_obj.save(update_fields=['created_at'])

        with self.assertRaisesMessage(ValueError, 'Token expirado'):
            verificar_magic_link(str(token_obj.token))
