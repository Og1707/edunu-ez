"""
Servicio de integración con n8n.

Centraliza el envío de datos al webhook de n8n y elimina la URL hardcodeada
que existía en api/webhooks.py. Toda la configuración se lee desde settings.py,
que a su vez la toma de variables de entorno.

Uso:
    from api.services.n8n_service import enviar_resultado_actividad, registrar_evento_actividad
"""

import json
import logging
from datetime import datetime
from threading import Thread

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_config() -> dict:
    """
    Lee la configuración de n8n desde settings en tiempo de ejecución.
    Leer en tiempo de ejecución (no al importar) permite que los tests
    puedan hacer override_settings sin problemas.
    """
    return {
        'url': getattr(settings, 'N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/Alumnos_settings'),
        'enabled': getattr(settings, 'N8N_WEBHOOK_ENABLED', True),
        'timeout': getattr(settings, 'N8N_WEBHOOK_TIMEOUT', 10),
        'retry_attempts': getattr(settings, 'N8N_WEBHOOK_RETRY_ATTEMPTS', 3),
    }


def _construir_payload(actividad_data: dict) -> dict:
    """
    Construye el payload estándar para el webhook de n8n.

    Parámetros:
        actividad_data: Dict con los datos de la actividad completada.

    Retorna:
        Dict listo para serializar a JSON y enviar al webhook.
    """
    return {
        'timestamp': datetime.now().isoformat(),
        'evento': 'actividad_completada',
        'datos': {
            'estudiante': {
                'id': actividad_data.get('estudiante_id'),
                'nombre': actividad_data.get('estudiante_nombre'),
                'email': actividad_data.get('estudiante_email'),
            },
            'actividad': {
                'id': actividad_data.get('actividad_id'),
                'titulo': actividad_data.get('actividad_titulo'),
                'tipo': actividad_data.get('actividad_tipo'),
            },
            'curso': {
                'id': actividad_data.get('curso_id'),
                'nombre': actividad_data.get('curso_nombre'),
            },
            'resultados': {
                'puntuacion': actividad_data.get('puntuacion', 0),
                'tiempo_empleado_minutos': actividad_data.get('tiempo_empleado', 0),
                'fecha_entrega': str(actividad_data.get('fecha_entrega', '')),
                'estado': actividad_data.get('estado', 'completada'),
                'es_tardia': actividad_data.get('es_tardia', False),
                'respuestas_detalle': actividad_data.get('respuestas_detalle', []),
            },
        },
    }


def enviar_resultado_actividad(actividad_data: dict, retry_attempts: int = None) -> dict:
    """
    Envía los resultados de una actividad completada al webhook de n8n (síncrono).

    Parámetros:
        actividad_data: Dict con los datos de la actividad completada.
            Claves esperadas: estudiante_id, estudiante_nombre, estudiante_email,
            actividad_id, actividad_titulo, actividad_tipo, curso_id, curso_nombre,
            puntuacion, tiempo_empleado, fecha_entrega, estado, es_tardia,
            respuestas_detalle (opcional).
        retry_attempts: Sobreescribe N8N_WEBHOOK_RETRY_ATTEMPTS si se especifica.

    Retorna:
        dict: {'success': bool, 'message': str, 'response_code': int}
    """
    config = _get_config()

    if not config['enabled']:
        logger.warning('Webhook de n8n deshabilitado (N8N_WEBHOOK_ENABLED=False)')
        return {'success': False, 'message': 'Webhook deshabilitado', 'response_code': 0}

    intentos = retry_attempts if retry_attempts is not None else config['retry_attempts']
    payload = _construir_payload(actividad_data)

    logger.info('Enviando resultado de actividad al webhook n8n: actividad_id=%s estudiante_id=%s',
                actividad_data.get('actividad_id'), actividad_data.get('estudiante_id'))

    for intento in range(intentos):
        try:
            response = requests.post(  # nosec B113
                config['url'],
                json=payload,
                timeout=config['timeout'],
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'EduNuñez-Django/1.0',
                },
            )

            logger.info('Respuesta webhook n8n (intento %d/%d): status=%s',
                        intento + 1, intentos, response.status_code)

            if response.status_code in (200, 201, 202, 204):
                return {
                    'success': True,
                    'message': f'Webhook enviado exitosamente (status {response.status_code})',
                    'response_code': response.status_code,
                }

            logger.warning('Webhook retornó status %s: %s',
                           response.status_code, response.text[:200])

            if intento < intentos - 1:
                continue

            return {
                'success': False,
                'message': f'Webhook retornó status {response.status_code}',
                'response_code': response.status_code,
            }

        except requests.exceptions.Timeout:
            logger.warning('Timeout en intento %d/%d al webhook n8n', intento + 1, intentos)
            if intento < intentos - 1:
                continue
            return {'success': False, 'message': 'Timeout en la conexión al webhook', 'response_code': 0}

        except requests.exceptions.ConnectionError as exc:
            logger.warning('Error de conexión en intento %d/%d: %s', intento + 1, intentos, exc)
            if intento < intentos - 1:
                continue
            return {'success': False, 'message': f'Error de conexión: {exc}', 'response_code': 0}

    return {'success': False, 'message': 'Falló después de todos los intentos', 'response_code': 0}


def enviar_resultado_actividad_async(actividad_data: dict) -> None:
    """
    Versión no-bloqueante de enviar_resultado_actividad.

    Lanza un daemon thread para el envío y retorna inmediatamente.
    El envío async usa retry_attempts=1 para evitar que el thread viva
    demasiado tiempo (1 intento × timeout = máximo N8N_WEBHOOK_TIMEOUT segundos).

    Parámetros:
        actividad_data: Dict con los datos de la actividad completada.
    """
    try:
        thread = Thread(
            target=enviar_resultado_actividad,
            kwargs={'actividad_data': actividad_data, 'retry_attempts': 1},
            daemon=True,
        )
        thread.start()
        logger.info('Envío de webhook n8n delegado a background thread')
    except Exception as exc:
        # Nunca debe romper el flujo principal
        logger.error('Error al lanzar thread de webhook n8n: %s', exc)


def registrar_evento_actividad(actividad_id: int, estudiante_id: int,
                                evento_tipo: str, datos_adicionales: dict = None) -> None:
    """
    Registra eventos de actividades para auditoría y debugging en el log.

    No realiza llamadas externas — solo registra en el logger del servidor.

    Parámetros:
        actividad_id: ID de la actividad.
        estudiante_id: ID del estudiante.
        evento_tipo: Tipo de evento ('iniciada', 'completada', 'fallida', etc.).
        datos_adicionales: Dict opcional con información extra del evento.
    """
    try:
        evento = {
            'timestamp': datetime.now().isoformat(),
            'actividad_id': actividad_id,
            'estudiante_id': estudiante_id,
            'evento_tipo': evento_tipo,
            'datos': datos_adicionales or {},
        }
        logger.info('Evento actividad registrado: %s', json.dumps(evento))
    except Exception as exc:
        logger.error('Error al registrar evento de actividad: %s', exc)
