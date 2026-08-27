"""
Tests para las vistas del sistema de plantillas de actividades.
"""
import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock

from api.models import Actividad, Curso, ActividadMultimedia, ActividadTexto, Pregunta, OpcionRespuesta

Usuario = get_user_model()


class TestVistasPlantillas(APITestCase):
    """Tests para las vistas de plantillas de actividades."""

    def setUp(self):
        """Configurar datos de prueba."""
        # Crear usuarios de prueba
        self.profesor = Usuario.objects.create_user(
            username='profesor_test',
            email='profesor@test.com',
            password='password123',
            rol='profesor',
            nombre_completo='Profesor Test'
        )

        self.estudiante = Usuario.objects.create_user(
            username='estudiante_test',
            email='estudiante@test.com',
            password='password123',
            rol='estudiante',
            nombre_completo='Estudiante Test'
        )

        # Crear curso de prueba
        self.curso = Curso.objects.create(
            nombre='Curso de Prueba',
            descripcion='Descripción del curso',
            profesor=self.profesor
        )

    @patch('api.views.templates.upload_multimedia_file')
    def test_crear_actividad_multimedia_exitoso(self, mock_upload):
        """Test creación exitosa de actividad multimedia."""
        # Mock de Cloudinary response
        mock_upload.return_value = {
            'secure_url': 'https://cloudinary.com/test/video.mp4',
            'file_type': 'video',
            'duration': 120.5,
            'bytes': 1024000,
            'public_id': 'test_video'
        }

        self.client.force_authenticate(user=self.profesor)

        data = {
            'titulo': 'Actividad Multimedia Test',
            'descripcion': 'Descripción de prueba',
            'tipo': 'multimedia',
            'curso': self.curso.id,
            'preguntas': [
                {
                    'enunciado': '¿Cuál es la capital de Francia?',
                    'orden': 1,
                    'opciones': [
                        {'texto': 'Madrid', 'es_correcta': False, 'orden': 1},
                        {'texto': 'París', 'es_correcta': True, 'orden': 2},
                        {'texto': 'Roma', 'es_correcta': False, 'orden': 3}
                    ]
                }
            ]
        }

        # Crear archivo mock
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile

        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )

        # Preparar datos con archivo
        data_with_file = {
            'titulo': 'Actividad Multimedia Test',
            'descripcion': 'Descripción de prueba',
            'tipo': 'multimedia',
            'curso': self.curso.id,
            'preguntas': json.dumps([
                {
                    'enunciado': '¿Cuál es la capital de Francia?',
                    'orden': 1,
                    'opciones': [
                        {'texto': 'Madrid', 'es_correcta': False, 'orden': 1},
                        {'texto': 'París', 'es_correcta': True, 'orden': 2},
                        {'texto': 'Roma', 'es_correcta': False, 'orden': 3}
                    ]
                }
            ]),
            'archivo_multimedia': video_file
        }

        response = self.client.post(
            reverse('crear_actividad_multimedia'),
            data_with_file,
            format='multipart'
        )

        # Verificar que se creó la actividad
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('actividad', response.data)
        self.assertEqual(response.data['actividad']['titulo'], 'Actividad Multimedia Test')

        # Verificar que se creó ActividadMultimedia
        actividad = Actividad.objects.get(titulo='Actividad Multimedia Test')
        multimedia = ActividadMultimedia.objects.get(actividad=actividad)
        self.assertEqual(multimedia.archivo_url_cloudinary, 'https://cloudinary.com/test/video.mp4')

    def test_crear_actividad_texto_exitoso(self):
        """Test creación exitosa de actividad de texto."""
        self.client.force_authenticate(user=self.profesor)

        data = {
            'titulo': 'Actividad Texto Test',
            'descripcion': 'Descripción de prueba',
            'tipo': 'texto',
            'curso': self.curso.id,
            'tiempo_limite_minutos': 30,
            'preguntas': [
                {
                    'enunciado': '¿Cuál es 2 + 2?',
                    'orden': 1,
                    'opciones': [
                        {'texto': '3', 'es_correcta': False, 'orden': 1},
                        {'texto': '4', 'es_correcta': True, 'orden': 2},
                        {'texto': '5', 'es_correcta': False, 'orden': 3}
                    ]
                }
            ]
        }

        response = self.client.post(
            reverse('crear_actividad_texto'),
            data,
            format='json'
        )

        # Verificar que se creó la actividad
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('actividad', response.data)

        # Verificar que se creó ActividadTexto
        actividad = Actividad.objects.get(titulo='Actividad Texto Test')
        texto = ActividadTexto.objects.get(actividad=actividad)
        self.assertEqual(texto.tiempo_limite_minutos, 30)

    def test_obtener_actividad_completa(self):
        """Test obtener actividad completa con preguntas."""
        # Crear actividad de prueba
        actividad = Actividad.objects.create(
            titulo='Actividad Completa Test',
            descripcion='Descripción',
            tipo='texto',
            template_type='texto',
            curso=self.curso,
            creado_por=self.profesor
        )

        # Crear pregunta
        pregunta = Pregunta.objects.create(
            actividad=actividad,
            enunciado='Pregunta de prueba',
            orden=1
        )

        # Crear opciones
        OpcionRespuesta.objects.create(
            pregunta=pregunta,
            texto='Opción 1',
            es_correcta=False,
            orden=1
        )
        OpcionRespuesta.objects.create(
            pregunta=pregunta,
            texto='Opción 2',
            es_correcta=True,
            orden=2
        )

        self.client.force_authenticate(user=self.profesor)

        response = self.client.get(
            reverse('obtener_actividad_completa', kwargs={'actividad_id': actividad.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Actividad Completa Test')
        self.assertEqual(len(response.data['preguntas']), 1)
        self.assertEqual(len(response.data['preguntas'][0]['opciones']), 2)

    def test_obtener_actividades_por_plantilla(self):
        """Test filtrar actividades por tipo de plantilla."""
        # Crear actividades de diferentes tipos
        Actividad.objects.create(
            titulo='Legacy Activity',
            descripcion='Descripción',
            tipo='legacy',
            template_type='legacy',
            curso=self.curso,
            creado_por=self.profesor
        )

        Actividad.objects.create(
            titulo='Multimedia Activity',
            descripcion='Descripción',
            tipo='multimedia',
            template_type='multimedia',
            curso=self.curso,
            creado_por=self.profesor
        )

        self.client.force_authenticate(user=self.profesor)

        response = self.client.get(
            reverse('obtener_actividades_por_plantilla') + '?template_type=multimedia'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['actividades']), 1)
        self.assertEqual(response.data['actividades'][0]['titulo'], 'Multimedia Activity')

    def test_permisos_insuficientes(self):
        """Test que estudiantes no puedan crear actividades."""
        self.client.force_authenticate(user=self.estudiante)

        data = {
            'titulo': 'Actividad No Autorizada',
            'descripcion': 'Descripción',
            'tipo': 'texto',
            'curso': self.curso.id,
            'preguntas': []
        }

        response = self.client.post(
            reverse('crear_actividad_texto'),
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('api.utils.cloudinary_utils.get_upload_signature')
    def test_obtener_firma_cloudinary(self, mock_signature):
        """Test obtener firma para uploads de Cloudinary."""
        mock_signature.return_value = {
            'signature': 'test_signature',
            'timestamp': '1234567890',
            'api_key': 'test_key'
        }

        self.client.force_authenticate(user=self.profesor)

        response = self.client.get(reverse('obtener_firma_cloudinary'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('signature', response.data)
        self.assertIn('timestamp', response.data)