"""
Configuración y clases personalizadas de Throttling (Rate Limiting) para EduNúñez.
"""

from rest_framework.throttling import ScopedRateThrottle, AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(ScopedRateThrottle):
    """
    Rate limiting específico para endpoints críticos de autenticación (Login / Registro / Magic Link).
    """
    scope = 'auth'


class CompleteActivityRateThrottle(ScopedRateThrottle):
    """
    Rate limiting para prevenir envíos masivos o scripts automatizados en la finalización de actividades.
    """
    scope = 'actividades_completar'
