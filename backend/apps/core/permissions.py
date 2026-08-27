from rest_framework import permissions


class EsProfesorDelCurso(permissions.BasePermission):
    """
    Permite el acceso solo a profesores asignados al curso específico o administradores.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, 'rol', None) == 'administrador' or request.user.is_staff:
            return True

        curso = getattr(obj, 'curso', obj)
        profesor_id = getattr(curso, 'profesor_id', None)
        return getattr(request.user, 'rol', None) == 'profesor' and profesor_id == request.user.id


class EsCreadorOAdministrador(permissions.BasePermission):
    """
    Permite lectura/escritura solo al creador del objeto o a un administrador.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if getattr(request.user, 'rol', None) == 'administrador' or request.user.is_staff:
            return True

        creado_por = getattr(obj, 'creado_por', getattr(obj, 'usuario', getattr(obj, 'estudiante', None)))
        return creado_por == request.user
