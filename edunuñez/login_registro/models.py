from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, password=None, **extra_fields):
        if not email:
            raise ValueError('El usuario debe tener un email')
        email = self.normalize_email(email)
        user = self.model(email=email, nombre=nombre, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nombre, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nombre, password, **extra_fields)

class usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100, default='123456')
    rol_user = [
        ('estudiante', 'Estudiante'),
        ('profesor', 'Profesor'),
        ('administrador', 'Administrador'),
    ]
    roles = models.CharField(max_length=20, choices=rol_user, default='estudiante')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

   
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    
    objects = UsuarioManager()

    def __str__(self):
        return self.nombre

