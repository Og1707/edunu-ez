"""
Tests adicionales para los endpoints REST del sistema de plantillas.
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


class TestTemplatesREST(APITestCase):
    """Tests para los endpoints REST adicionales de plantillas."""

    def setUp(self):
        """Configurar datos de prueba."""
        # Crear usuarios de prueba
        self.admin = Usuario.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            rol='administrador',
            nombre_completo='Admin Test'
        )

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

        # Crear actividad de prueba
        self.actividad = Actividad.objects.create(
            titulo='Actividad de Prueba',
            descripcion='Descripción',
            tipo='texto',
            template_type='texto',
            curso=self.curso,
            creado_por=self.profesor
        )

        # Crear pregunta de prueba
        self.pregunta = Pregunta.objects.create(
            actividad=self.actividad,
            enunciado='¿Cuál es 2 + 2?',
            orden=1
        )

        # Crear opciones de respuesta
        OpcionRespuesta.objects.create(
            pregunta=self.pregunta,
            texto='3',
            es_correcta=False,
            orden=1
        )
        OpcionRespuesta.objects.create(
            pregunta=self.pregunta,
            texto='4',
            es_correcta=True,
            orden=2
        )

    def test_listar_plantillas_disponibles(self):
        """Test listar plantillas disponibles."""
        self.client.force_authenticate(user=self.profesor)
        response = self.client.get(reverse('listar_plantillas_disponibles'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('plantillas', response.data)
        self.assertIn('multimedia', response.data['plantillas'])
        self.assertIn('texto', response.data['plantillas'])
        self.assertIn('legacy', response.data['plantillas'])

    def test_preview_plantilla_multimedia_valido(self):
        """Test preview de plantilla multimedia con datos válidos."""
        self.client.force_authenticate(user=self.profesor)
        
        preguntas_json = json.dumps([
            {
                'enunciado': '¿Cuál es la capital de Francia?',
                'orden': 1,
                'opciones': [
                    {'texto': 'Madrid', 'es_correcta': False, 'orden': 1},
                    {'texto': 'París', 'es_correcta': True, 'orden': 2}
                ]
            }
        ])

        response = self.client.get(
            reverse('preview_plantilla_multimedia'),
            {
                'titulo': 'Actividad Test',
                'descripcion': 'Descripción test',
                'preguntas': preguntas_json
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valido'])
        self.assertEqual(response.data['preguntas_count'], 1)
        self.assertEqual(response.data['opciones_total'], 2)

    def test_preview_plantilla_multimedia_invalido(self):
        """Test preview de plantilla multimedia con datos inválidos."""
        self.client.force_authenticate(user=self.profesor)

        preguntas_json = json.dumps([
            {
                'enunciado': 'Pregunta sin opciones',
                'orden': 1,
                'opciones': []  # Inválido: debe tener al menos 2 opciones
            }
        ])

        response = self.client.get(
            reverse('preview_plantilla_multimedia'),
            {
                'titulo': 'Actividad Test',
                'preguntas': preguntas_json
            }
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valido'])
        self.assertIn('errores', response.data)

    def test_duplicar_actividad_texto(self):
        """Test duplicar actividad de texto."""
        self.client.force_authenticate(user=self.profesor)

        response = self.client.post(
            reverse('duplicar_actividad', kwargs={'actividad_id': self.actividad.id})
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('nueva_actividad', response.data)
        self.assertIn('actividad_original', response.data)
        
        # Verificar que la nueva actividad tiene "Copia" en el título
        nueva_actividad = response.data['nueva_actividad']
        self.assertIn('Copia', nueva_actividad['titulo'])
        
        # Verificar que se duplicaron las preguntas
        self.assertEqual(len(nueva_actividad['preguntas']), 1)
        self.assertEqual(len(nueva_actividad['preguntas'][0]['opciones']), 2)

    def test_duplicar_actividad_multimedia_requiere_archivo(self):
        """Test duplicar actividad multimedia requiere nuevo archivo."""
        # Crear actividad multimedia
        actividad_multimedia = Actividad.objects.create(
            titulo='Actividad Multimedia',
            descripcion='Descripción',
            tipo='video',
            template_type='multimedia',
            curso=self.curso,
            creado_por=self.profesor
        )

        ActividadMultimedia.objects.create(
            actividad=actividad_multimedia,
            archivo_url_cloudinary='https://test.com/video.mp4',
            tipo_archivo='video'
        )

        self.client.force_authenticate(user=self.profesor)

        response = self.client.post(
            reverse('duplicar_actividad', kwargs={'actividad_id': actividad_multimedia.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('actividad_original', response.data)
        self.assertIn('mensaje', response.data)
        self.assertIn('requiere un nuevo archivo', response.data['mensaje'])

    def test_duplicar_actividad_sin_permisos(self):
        """Test duplicar actividad sin permisos."""
        self.client.force_authenticate(user=self.estudiante)

        response = self.client.post(
            reverse('duplicar_actividad', kwargs={'actividad_id': self.actividad.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_estadisticas_plantillas_admin(self):
        """Test obtener estadísticas como administrador."""
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('estadisticas_plantillas'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('generales', response.data)
        self.assertIn('por_tipo_plantilla', response.data)
        self.assertIn('total_actividades', response.data['generales'])

    def test_estadisticas_plantillas_no_admin(self):
        """Test obtener estadísticas sin ser administrador."""
        self.client.force_authenticate(user=self.profesor)

        response = self.client.get(reverse('estadisticas_plantillas'))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_buscar_actividades_con_query(self):
        """Test buscar actividades con término de búsqueda."""
        self.client.force_authenticate(user=self.profesor)

        response = self.client.get(
            reverse('buscar_actividades_plantillas'),
            {'q': 'Prueba'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['query'], 'Prueba')

    def test_buscar_actividades_con_filtros(self):
        """Test buscar actividades con filtros."""
        self.client.force_authenticate(user=self.profesor)

        response = self.client.get(
            reverse('buscar_actividades_plantillas'),
            {
                'template_type': 'texto',
                'curso_id': self.curso.id
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(response.data['filtros']['template_type'], 'texto')

    def test_buscar_actividades_estudiante_limitadas(self):
        """Test buscar actividades como estudiante (solo asignadas)."""
        self.client.force_authenticate(user=self.estudiante)

        response = self.client.get(
            reverse('buscar_actividades_plantillas'),
            {'q': 'Prueba'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Estudiante solo debe ver actividades asignadas (ninguna en este caso)
        self.assertEqual(len(response.data['results']), 0)

    def test_buscar_actividades_paginacion(self):
        """Test paginación en búsqueda de actividades."""
        self.client.force_authenticate(user=self.profesor)

        # Crear más actividades para probar paginación
        for i in range(15):
            Actividad.objects.create(
                titulo=f'Actividad {i}',
                descripcion='Descripción',
                tipo='texto',
                template_type='texto',
                curso=self.curso,
                creado_por=self.profesor
            )

        response = self.client.get(
            reverse('buscar_actividades_plantillas'),
            {'page': 1, 'page_size': 10}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertLessEqual(len(response.data['results']), 10)
