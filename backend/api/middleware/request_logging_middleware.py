"""
Middleware de Logging Estructurado JSON para rastreo contextual de peticiones y respuestas.
Genera un identificador único (X-Request-ID) por cada petición entrante.
"""

import time
import uuid
import logging

logger = logging.getLogger('api.requests')


class RequestLoggingMiddleware:
    """
    Middleware para enriquecer las peticiones HTTP con un request_id y registrar
    el ciclo de vida completo de cada llamada a la API en formato JSON estructurado.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Asignar o propagar Request ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.request_id = request_id

        # Capturar tiempo de inicio
        start_time = time.time()

        # Obtener información del usuario si está autenticado
        user_id = getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None
        username = getattr(request.user, 'username', 'anonymous') if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'

        logger.info(
            "HTTP Request Incoming: %s %s",
            request.method, request.path,
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'user_id': user_id,
                'username': username,
                'event': 'request_started',
            }
        )

        # 2. Procesar la petición
        response = self.get_response(request)

        # 3. Calcular duración
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Inyectar X-Request-ID en la cabecera de la respuesta
        response['X-Request-ID'] = request_id

        # Determinar nivel de log según código de estado
        log_method = logger.info
        if response.status_code >= 500:
            log_method = logger.error
        elif response.status_code >= 400:
            log_method = logger.warning

        log_method(
            "HTTP Response Completed: %s %s -> %d (%s ms)",
            request.method, request.path, response.status_code, duration_ms,
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') and request.user.is_authenticated else None,
                'event': 'request_finished',
            }
        )

        return response

    def process_exception(self, request, exception):
        """Captura excepciones no manejadas antes de que retornen 500."""
        request_id = getattr(request, 'request_id', 'unknown')
        logger.error(
            "Unhandled Exception in request %s %s: %s",
            request.method, request.path, str(exception),
            exc_info=True,
            extra={
                'request_id': request_id,
                'method': request.method,
                'path': request.path,
                'exception_type': exception.__class__.__name__,
                'event': 'request_exception',
            }
        )
        return None
