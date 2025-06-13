from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import usuario

class UsuarioAdmin(UserAdmin):
    model = usuario
    list_display = ('email', 'nombre', 'roles', 'is_staff', 'is_superuser')
    list_filter = ('roles', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'nombre', 'password', 'roles', 'is_staff', 'is_superuser', 'is_active')}),
        ('Permisos', {'fields': ('groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'password', 'roles', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )
    search_fields = ('email', 'nombre')
    ordering = ('email',)

admin.site.register(usuario, UsuarioAdmin)