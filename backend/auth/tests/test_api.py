from datetime import timedelta
from django.test import override_settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from auth.models import MagicLinkToken, Invitation


User = get_user_model()


class MagicLinkIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='usuario2',
            email='usuario2@example.com',
            password='Password123!'
        )
        self.client = APIClient()

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_magic_link_happy_path(self):
        response = self.client.post('/auth/magic-link/', {'email': self.user.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token_obj = MagicLinkToken.objects.get(user=self.user)

        verify_response = self.client.get(f'/auth/magic-link/verify/?token={token_obj.token}')
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', verify_response.data)

    def test_magic_link_token_expirado_retornara_400(self):
        token_obj = MagicLinkToken.objects.create(user=self.user)
        token_obj.created_at = timezone.now() - timedelta(minutes=16)
        token_obj.save(update_fields=['created_at'])

        response = self.client.get(f'/auth/magic-link/verify/?token={token_obj.token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Token expirado')

    def test_invitacion_rate_limit_por_usuario(self):
        self.client.force_authenticate(user=self.user)
        for index in range(10):
            payload = {'email': f'invitado{index}@example.com'}
            response = self.client.post('/auth/invitaciones/', payload, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post('/auth/invitaciones/', {'email': 'limite@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(response.data['detail'], 'Límite de invitaciones alcanzado. Intenta en 1 hora.')

    def test_invitacion_idor_retorna_403(self):
        owner = User.objects.create_user(
            username='dueño',
            email='dueno@example.com',
            password='Password123!'
        )
        invitation = Invitation.objects.create(created_by=owner, email='victima@example.com')
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f'/auth/invitaciones/{invitation.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
