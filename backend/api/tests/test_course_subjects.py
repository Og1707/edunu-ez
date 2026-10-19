from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Asignatura, Curso, Usuario


class CourseSubjectsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Usuario.objects.create_user(
            username='subjects_admin', email='subjects_admin@test.local', password='pass', rol='administrador'
        )
        self.teacher = Usuario.objects.create_user(
            username='subjects_teacher', email='subjects_teacher@test.local', password='pass', rol='profesor'
        )
        self.course = Curso.objects.create(nombre='Grupo A1', profesor=self.teacher)
        self.math = Asignatura.objects.get(nombre='Matemáticas')
        self.language = Asignatura.objects.get(nombre='Lenguaje')

    def test_crear_curso_asigna_varias_asignaturas_y_las_expone_en_listado(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/cursos/crear/', {
            'nombre': 'Grupo A2',
            'descripcion': 'Curso de prueba',
            'profesor': self.teacher.id,
            'asignaturas': [self.math.id, self.language.id],
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertCountEqual(response.data['asignaturas_nombres'], ['Matemáticas', 'Lenguaje'])

        listed = self.client.get('/api/cursos/')
        course_data = next(item for item in listed.data if item['id'] == response.data['id'])
        self.assertCountEqual(course_data['asignaturas_nombres'], ['Matemáticas', 'Lenguaje'])

    def test_editar_curso_reemplaza_asignaturas_solo_si_se_envian(self):
        self.course.asignaturas.add(self.math)
        self.client.force_authenticate(self.teacher)
        response = self.client.put(f'/api/cursos/{self.course.id}/gestionar/', {
            'asignaturas': [self.language.id],
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['asignaturas_nombres'], ['Lenguaje'])

    def test_administrador_puede_agregar_asignatura_y_profesor_solo_consultarlas(self):
        self.client.force_authenticate(self.teacher)
        listed = self.client.get('/api/asignaturas/')
        self.assertEqual(listed.status_code, 200)
        denied = self.client.post('/api/asignaturas/', {'nombre': 'Música'}, format='json')
        self.assertEqual(denied.status_code, 403)

        self.client.force_authenticate(self.admin)
        created = self.client.post('/api/asignaturas/', {'nombre': 'Música'}, format='json')
        self.assertEqual(created.status_code, 201)
        duplicate = self.client.post('/api/asignaturas/', {'nombre': 'Música'}, format='json')
        self.assertEqual(duplicate.status_code, 400)

    def test_rechaza_asignatura_inexistente_al_crear_curso(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/cursos/crear/', {
            'nombre': 'Grupo Inválido',
            'asignaturas': [999999],
        }, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Curso.objects.filter(nombre='Grupo Inválido').exists())
