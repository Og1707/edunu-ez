"""
Manejador global de excepciones para Django REST Framework.
Captura excepciones de negocio personalizadas y estandariza las respuestas de error.
"""

import logging
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status
from api.exceptions import EduNuñezException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Handler global que intercepta EduNuñezException, excepciones de DRF
    y errores no controlados (500).
    """
    # 1. Manejo de excepciones de negocio de EduNúñez
    if isinstance(exc, EduNuñezException):
        view = context.get('view')
        view_name = view.__class__.__name__ if view else 'UnknownView'
        logger.warning(
            "Excepción de negocio [%s] en %s: %s (status=%d)",
            exc.code, view_name, exc.message, exc.status_code,
            extra={
                'error_code': exc.code,
                'status_code': exc.status_code,
                'details': exc.details,
                'view': view_name,
            }
        )
        return Response(exc.to_dict(), status=exc.status_code)

    # 2. Llamada al manejador por defecto de DRF
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Estandarizar la estructura para DRF manteniendo retrocompatibilidad total
        custom_data = dict(response.data) if isinstance(response.data, dict) else {}
        custom_data["error"] = {
            "codigo": getattr(exc, 'default_code', 'ERROR_CLIENTE'),
            "mensaje": "Error en la petición",
            "detalles": response.data,
        }
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_data["mensaje"] = str(response.data['detail'])
                custom_data["error"]["mensaje"] = str(response.data['detail'])
                custom_data["detail"] = response.data['detail']
            elif 'mensaje' in response.data:
                custom_data["mensaje"] = str(response.data['mensaje'])
                custom_data["error"]["mensaje"] = str(response.data['mensaje'])
            else:
                custom_data.setdefault("mensaje", "Datos de entrada inválidos")
        else:
            custom_data["mensaje"] = str(response.data)

        response.data = custom_data
        return response

    # 3. Errores no capturados por DRF (500 Internal Server Error)
    request = context.get('request')
    path = request.path if request else 'Unknown'
    method = request.method if request else 'Unknown'

    logger.error(
        "Error no controlado 500 en %s %s: %s",
        method, path, str(exc),
        exc_info=True,
        extra={
            'path': path,
            'method': method,
            'exception_type': exc.__class__.__name__,
        }
    )

    return Response(
        {
            "error": {
                "codigo": "ERROR_INTERNO_SERVIDOR",
                "mensaje": "Ocurrió un error interno en el servidor. Por favor, intenta de nuevo más tarde.",
            },
            "mensaje": f"Error interno: {str(exc)}",
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
