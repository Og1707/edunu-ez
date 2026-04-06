from django.core.exceptions import FieldDoesNotExist
from rest_framework.permissions import BasePermission


class OwnerQuerysetMixin:
    owner_field = 'user'

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user or not self.request.user.is_authenticated:
            return queryset.none()

        if getattr(self, 'action', None) == 'list':
            return queryset.filter(**{self.owner_field: self.request.user})

        return queryset


class IsOwnerOrDeny(BasePermission):
    owner_field = 'user'

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        owner_value = obj
        for field in self.owner_field.split('__'):
            try:
                owner_value = getattr(owner_value, field)
            except AttributeError:
                return False
        return owner_value == request.user
