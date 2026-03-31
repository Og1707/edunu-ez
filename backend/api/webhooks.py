"""
Módulo de webhooks para integración con n8n y otros servicios.
Maneja el envío de datos a endpoints externos de forma asincrónica.
"""

import json
import requests
import logging
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuración de webhooks
WEBHOOKS_CONFIG = {
    'n8n_alumnos': {
        'url': 'http://localhost:5678/webhook/Alumnos_settings',
        'timeout': 10,
        'retry_attempts': 3,
        'enabled': True
    }
}


def enviar_resultado_actividad_a_n8n(actividad_completada_data):
    """
    Envía los resultados de una actividad completada al webhook de n8n.
    
    Args:
        actividad_completada_data (dict): Diccionario con los datos de la actividad completada
        
    Estructura esperada:
        {
            'estudiante_id': int,
            'estudiante_nombre': str,
            'estudiante_email': str,
            'actividad_id': int,
            'actividad_titulo': str,
            'actividad_tipo': str,
            'curso_id': int,
            'curso_nombre': str,
            'puntuacion': float,
            'tiempo_empleado': int,  # en minutos
            'fecha_entrega': datetime,
            'estado': str,
            'es_tardia': bool,
            'respuestas_detalle': list  # Lista de respuestas individuales (opcional)
        }
    
    Returns:
        dict: Resultado del envío {'success': bool, 'message': str, 'response_code': int}
    """
    
    webhook_config = WEBHOOKS_CONFIG.get('n8n_alumnos')
    
    if not webhook_config.get('enabled'):
        logger.warning('Webhook de n8n está deshabilitado')
        return {
            'success': False,
            'message': 'Webhook deshabilitado',
            'response_code': 0
        }
    
    try:
        # Preparar datos para enviar
        payload = {
            'timestamp': datetime.now().isoformat(),
            'evento': 'actividad_completada',
            'datos': {
                'estudiante': {
                    'id': actividad_completada_data.get('estudiante_id'),
                    'nombre': actividad_completada_data.get('estudiante_nombre'),
                    'email': actividad_completada_data.get('estudiante_email')
                },
                'actividad': {
                    'id': actividad_completada_data.get('actividad_id'),
                    'titulo': actividad_completada_data.get('actividad_titulo'),
                    'tipo': actividad_completada_data.get('actividad_tipo')
                },
                'curso': {
                    'id': actividad_completada_data.get('curso_id'),
                    'nombre': actividad_completada_data.get('curso_nombre')
                },
                'resultados': {
                    'puntuacion': actividad_completada_data.get('puntuacion', 0),
                    'tiempo_empleado_minutos': actividad_completada_data.get('tiempo_empleado', 0),
                    'fecha_entrega': str(actividad_completada_data.get('fecha_entrega', '')),
                    'estado': actividad_completada_data.get('estado', 'completada'),
                    'es_tardia': actividad_completada_data.get('es_tardia', False),
                    'respuestas_detalle': actividad_completada_data.get('respuestas_detalle', [])  # Incluir respuestas
                }
            }
        }
        
        logger.info(f"Enviando resultado de actividad al webhook de n8n: {json.dumps(payload, indent=2)}")
        
        # Enviar request con reintentos
        for intento in range(webhook_config.get('retry_attempts', 1)):
            try:
                response = requests.post(
                    webhook_config['url'],
                    json=payload,
                    timeout=webhook_config.get('timeout', 10),
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'EduNuñez-Django/1.0'
                    }
                )
                
                logger.info(f"Respuesta del webhook n8n (intento {intento + 1}): "
                           f"Status={response.status_code}, Body={response.text[:500]}")
                
                if response.status_code in [200, 201, 202, 204]:
                    logger.info(f"Resultado de actividad enviado exitosamente a n8n. "
                              f"Status: {response.status_code}")
                    
                    return {
                        'success': True,
                        'message': f'Webhook enviado exitosamente (status {response.status_code})',
                        'response_code': response.status_code,
                        'response_body': response.text[:1000]  # Primeros 1000 caracteres
                    }
                else:
                    logger.warning(f"Webhook retornó status {response.status_code}: {response.text[:200]}")
                    
                    if intento < webhook_config.get('retry_attempts', 1) - 1:
                        logger.info(f"Reintentando envío ({intento + 1}/{webhook_config.get('retry_attempts')})")
                        continue
                    else:
                        return {
                            'success': False,
                            'message': f'Webhook retornó status {response.status_code}',
                            'response_code': response.status_code
                        }
                        
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout en intento {intento + 1} de envío a webhook n8n")
                if intento < webhook_config.get('retry_attempts', 1) - 1:
                    continue
                else:
                    return {
                        'success': False,
                        'message': 'Timeout en la conexión al webhook',
                        'response_code': 0
                    }
                    
            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Error de conexión en intento {intento + 1}: {str(e)}")
                if intento < webhook_config.get('retry_attempts', 1) - 1:
                    continue
                else:
                    return {
                        'success': False,
                        'message': f'Error de conexión: {str(e)}',
                        'response_code': 0
                    }
        
        return {
            'success': False,
            'message': 'Falló después de varios intentos',
            'response_code': 0
        }
        
    except Exception as e:
        logger.error(f"Error al enviar resultado de actividad a webhook n8n: {str(e)}")
        
        return {
            'success': False,
            'message': f'Error interno: {str(e)}',
            'response_code': 0
        }


def enviar_resultado_actividad_n8n_async(actividad_completada_data):
    """
    Versión asincrónica (no-bloqueante) de enviar resultado a webhook.
    Se ejecuta en background sin esperar respuesta.
    
    Args:
        actividad_completada_data (dict): Datos de la actividad completada
    """
    try:
        # Importar aquí para evitar circular imports
        from django.core.management import call_command
        from threading import Thread
        
        # Crear un thread para enviar el webhook en background
        thread = Thread(
            target=enviar_resultado_actividad_a_n8n,
            args=(actividad_completada_data,),
            daemon=True
        )
        thread.start()
        
        logger.info("Webhook enviado a background")
        
    except Exception as e:
        logger.error(f"Error al iniciar thread de webhook: {str(e)}")


def registrar_evento_actividad(actividad_id, estudiante_id, evento_tipo, datos_adicionales=None):
    """
    Registra eventos de actividades para auditoría y debugging.
    
    Args:
        actividad_id (int): ID de la actividad
        estudiante_id (int): ID del estudiante
        evento_tipo (str): Tipo de evento (iniciada, completada, fallida, etc)
        datos_adicionales (dict): Datos adicionales del evento
    """
    try:
        evento = {
            'timestamp': datetime.now().isoformat(),
            'actividad_id': actividad_id,
            'estudiante_id': estudiante_id,
            'evento_tipo': evento_tipo,
            'datos': datos_adicionales or {}
        }
        
        logger.info(f"Evento registrado: {json.dumps(evento)}")
        
    except Exception as e:
        logger.error(f"Error al registrar evento: {str(e)}")
