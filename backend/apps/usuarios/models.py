from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROLES = [
        ('administrador', 'Administrador'),
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='estudiante')
    nombre_completo = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    class Meta:
        db_table = 'api_usuario'

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
