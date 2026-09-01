import hashlib
from unittest.mock import Mock, patch

from django.test import override_settings

from api.services.n8n_service import enviar_resultado_actividad
from api.utils.cloudinary_utils import get_upload_signature


@override_settings(
    N8N_WEBHOOK_URL='https://example.com/webhook',
    N8N_WEBHOOK_ENABLED=True,
    N8N_WEBHOOK_TIMEOUT=7,
    N8N_WEBHOOK_RETRY_ATTEMPTS=1,
)
@patch('api.services.n8n_service.requests.post')
def test_enviar_resultado_actividad_uses_configured_timeout(mock_post):
    mock_post.return_value = Mock(status_code=200, text='ok')

    resultado = enviar_resultado_actividad(
        {
            'estudiante_id': 1,
            'estudiante_nombre': 'Estudiante',
            'estudiante_email': 'estudiante@example.com',
            'actividad_id': 99,
            'actividad_titulo': 'Actividad',
            'actividad_tipo': 'quiz',
            'curso_id': 10,
            'curso_nombre': 'Curso',
        }
    )

    assert resultado['success'] is True
    assert mock_post.call_args.kwargs['timeout'] == 7


@override_settings(CLOUDINARY_API_SECRET='secret')
@patch('api.utils.cloudinary_utils.cloudinary.config')
@patch('time.time', return_value=123)
def test_get_upload_signature_preserves_expected_sha1_signature(_mock_time, mock_config):
    mock_config.return_value = Mock(api_key='api_key', cloud_name='demo')

    firma = get_upload_signature()
    esperado = hashlib.sha1(b'timestamp=123secret').hexdigest()

    assert firma == {
        'signature': esperado,
        'timestamp': 123,
        'api_key': 'api_key',
        'cloud_name': 'demo',
    }
