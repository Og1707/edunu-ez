"""
Tests para validar los endpoints de autenticación y permisos en api/views/auth.py.
"""
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from apps.usuarios.models import Usuario


class TestListarUsuariosPorRol(TestCase):
    """
    Tests para endpoint GET /api/usuarios/listar/
    Valida autenticación y permisos por rol.
    """
    
    def setUp(self):
        self.client = APIClient()
        self.endpoint = '/api/usuarios/listar/'
        
        self.admin = Usuario.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='pass123',
            rol='administrador',
            nombre_completo='Admin Test'
        )
        
        self.profesor = Usuario.objects.create(
            username='profesor_test',
            email='profesor@test.com',
            password='pass123',
            rol='profesor',
            nombre_completo='Profesor Test'
        )
        
        self.estudiante = Usuario.objects.create(
            username='estudiante_test',
            email='estudiante@test.com',
            password='pass123',
            rol='estudiante',
            nombre_completo='Estudiante Test'
        )
    
    def test_sin_autenticacion_retorna_401_o_403(self):
        """
        Petición no autenticada debe ser rechazada con 401 o 403.
        """
        response = self.client.get(self.endpoint)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_profesor_ve_estudiantes(self):
        """
        Profesor autenticado solo ve usuarios con rol estudiante.
        """
        self.client.force_authenticate(user=self.profesor)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [u['username'] for u in response.data]
        self.assertIn('estudiante_test', usernames)
        self.assertNotIn('profesor_test', usernames)
        self.assertNotIn('admin_test', usernames)
    
    def test_admin_ve_todos(self):
        """
        Admin autenticado ve todos los usuarios.
        """
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [u['username'] for u in response.data]
        self.assertIn('estudiante_test', usernames)
        self.assertIn('profesor_test', usernames)
        self.assertIn('admin_test', usernames)
    
    def test_estudiante_no_tiene_permisos_403(self):
        """
        Estudiante autenticado no tiene permisos para listar usuarios (403 Forbidden).
        """
        self.client.force_authenticate(user=self.estudiante)
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestObtenerActividadesProfesor(TestCase):
    """
    Tests para endpoint de actividades del profesor.
    """
    
    def setUp(self):
        self.client = APIClient()
        self.endpoint = '/api/actividades/profesor/'
        
        self.profesor = Usuario.objects.create(
            username='profesor_act',
            email='profesor_act@test.com',
            password='pass123',
            rol='profesor'
        )
    
    def test_profesor_sin_cursos_retorna_200_array_vacio(self):
        self.client.force_authenticate(user=self.profesor)
        response = self.client.get(self.endpoint, {'user_id': self.profesor.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 0)
    
    def test_sin_autenticacion_retorna_error(self):
        response = self.client.get(self.endpoint)
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
