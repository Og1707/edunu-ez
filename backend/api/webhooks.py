"""
Módulo de compatibilidad — webhooks.py

DEPRECADO: Este módulo existía con la lógica de webhooks hardcodeada.
La lógica ha sido migrada a api/services/n8n_service.py, que lee la
configuración desde settings.py (variables de entorno).

Este archivo re-exporta las funciones del nuevo servicio para no romper
importaciones existentes. Será eliminado una vez que todas las vistas
importen directamente desde api.services.n8n_service.

Migración:
    # Antes
    from api.webhooks import enviar_resultado_actividad_a_n8n, registrar_evento_actividad

    # Después
    from api.services.n8n_service import enviar_resultado_actividad, registrar_evento_actividad
"""

from api.services.n8n_service import (
    enviar_resultado_actividad as enviar_resultado_actividad_a_n8n,
    enviar_resultado_actividad_async as enviar_resultado_actividad_n8n_async,
    registrar_evento_actividad,
)

__all__ = [
    'enviar_resultado_actividad_a_n8n',
    'enviar_resultado_actividad_n8n_async',
    'registrar_evento_actividad',
]
