"""
Jerarquía de excepciones de negocio para la plataforma EduNúñez.

Permite a los servicios desacoplarse del framework HTTP lanzando excepciones
semánticas y tipadas que el Global Exception Handler transformará en respuestas
HTTP estructuradas.
"""


class EduNuñezException(Exception):
    """
    Excepción base para todas las reglas de negocio de EduNúñez.
    """
    default_message = "Ha ocurrido un error en la operación."
    default_code = "ERROR_NEGOCIO"
    default_status_code = 400

    def __init__(self, message: str = None, code: str = None, status_code: int = None, details: dict = None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.status_code = status_code or self.default_status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        payload = {
            "error": {
                "codigo": self.code,
                "mensaje": self.message,
            }
        }
        if self.details:
            payload["error"]["detalles"] = self.details
        # Mantener retrocompatibilidad con clientes que esperan 'mensaje' en la raíz
        payload["mensaje"] = self.message
        return payload


class ResourceNotFoundException(EduNuñezException):
    """Recurso no encontrado (HTTP 404)."""
    default_message = "El recurso solicitado no existe o no fue encontrado."
    default_code = "RECURSO_NO_ENCONTRADO"
    default_status_code = 404


class BusinessValidationException(EduNuñezException):
    """Error en reglas de validación de negocio (HTTP 400)."""
    default_message = "Los datos proporcionados no cumplen con las reglas de negocio."
    default_code = "ERROR_VALIDACION_NEGOCIO"
    default_status_code = 400


class PermissionDeniedBusinessException(EduNuñezException):
    """Acceso o acción denegada por reglas de negocio o rol (HTTP 403)."""
    default_message = "No tienes permisos para realizar esta acción sobre el recurso."
    default_code = "PERMISO_DENEGADO"
    default_status_code = 403


class ConflictBusinessException(EduNuñezException):
    """Conflicto con el estado actual del recurso (HTTP 409)."""
    default_message = "La operación entra en conflicto con el estado actual del recurso."
    default_code = "CONFLICTO_ESTADO"
    default_status_code = 409
