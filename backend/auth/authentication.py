"""
Clase de autenticación JWT — EduNúñez.

Delega la validación del token al backend de djangorestframework-simplejwt.
Se mantiene el nombre JWTAuthentication para no tocar todos los @authentication_classes
distribuidos por las vistas; es un alias transparente.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication  # noqa: F401

# Re-exportamos con el mismo nombre que usaba la clase manual.
# Todas las vistas que hacen `from auth.authentication import JWTAuthentication`
# siguen funcionando sin cambios.
__all__ = ["JWTAuthentication"]
