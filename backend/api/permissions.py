from rest_framework.permissions import BasePermission


class IsProfesor(BasePermission):
    message = 'Debes ser profesor.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(
            user
            and user.is_authenticated
            and getattr(user, 'rol', None) == 'profesor'
        )


class IsAdministrador(BasePermission):
    message = 'Debes ser administrador.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        return bool(
            user
            and user.is_authenticated
            and getattr(user, 'rol', None) == 'administrador'
        )


class IsOwner(BasePermission):
    message = 'Debes ser el propietario del recurso.'

    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not (user and user.is_authenticated):
            return False

        kwargs = getattr(request, 'parser_context', {}).get('kwargs', {})
        target_user_id = kwargs.get('user_id')
        if target_user_id is None:
            return True

        return str(user.id) == str(target_user_id)
