from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Actividad, AsignacionActividad, Curso, EstudianteCurso, Usuario


class DashboardEndpointTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = Usuario.objects.create_user(
            username='dashboard_admin', email='dashboard_admin@test.local', password='pass', rol='administrador'
        )
        self.teacher = Usuario.objects.create_user(
            username='dashboard_teacher', email='dashboard_teacher@test.local', password='pass', rol='profesor'
        )
        self.other_teacher = Usuario.objects.create_user(
            username='dashboard_other_teacher', email='dashboard_other@test.local', password='pass', rol='profesor'
        )
        self.student = Usuario.objects.create_user(
            username='dashboard_student', email='dashboard_student@test.local', password='pass', rol='estudiante'
        )
        self.other_student = Usuario.objects.create_user(
            username='dashboard_other_student', email='dashboard_other_student@test.local', password='pass', rol='estudiante'
        )
        self.course = Curso.objects.create(nombre='Curso Dashboard A', profesor=self.teacher)
        self.other_course = Curso.objects.create(nombre='Curso Dashboard B', profesor=self.other_teacher)
        EstudianteCurso.objects.create(curso=self.course, estudiante=self.student)
        EstudianteCurso.objects.create(curso=self.other_course, estudiante=self.other_student)
        self.activity = Actividad.objects.create(
            titulo='Actividad del curso A', descripcion='', curso=self.course, creado_por=self.teacher
        )
        self.other_activity = Actividad.objects.create(
            titulo='Actividad del curso B', descripcion='', curso=self.other_course, creado_por=self.other_teacher
        )
        AsignacionActividad.objects.create(
            actividad=self.activity, estudiante=self.student, profesor=self.teacher,
            estado='calificada', calificacion=84,
        )
        AsignacionActividad.objects.create(
            actividad=self.other_activity, estudiante=self.other_student, profesor=self.other_teacher,
            estado='calificada', calificacion=20,
        )

    def test_profesor_solo_recibe_su_alcance_y_su_detalle(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get('/api/dashboard/resumen/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data['cursos']], [self.course.id])
        self.assertEqual([item['id'] for item in response.data['estudiantes']], [self.student.id])
        self.assertEqual(response.data['kpis']['promedio'], 84.0)

        detail = self.client.get(f'/api/dashboard/estudiantes/{self.student.id}/')
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['promedio'], 84.0)

    def test_profesor_no_puede_consultar_perfil_de_otro_profesor(self):
        self.client.force_authenticate(self.teacher)
        response = self.client.get(f'/api/dashboard/estudiantes/{self.other_student.id}/')
        self.assertEqual(response.status_code, 404)

    def test_administrador_ve_datos_globales(self):
        Usuario.objects.create_user(
            username='dashboard_unenrolled', email='dashboard_unenrolled@test.local', password='pass', rol='estudiante'
        )
        self.client.force_authenticate(self.admin)
        response = self.client.get('/api/dashboard/resumen/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['kpis']['cursos'], 2)
        self.assertEqual(response.data['kpis']['estudiantes'], 3)
        self.assertEqual(response.data['kpis']['profesores'], 2)

    def test_estudiante_no_tiene_acceso_al_dashboard_de_personal(self):
        self.client.force_authenticate(self.student)
        response = self.client.get('/api/dashboard/resumen/')
        self.assertEqual(response.status_code, 403)

    def test_resumen_requiere_autenticacion(self):
        response = self.client.get('/api/dashboard/resumen/')
        self.assertIn(response.status_code, (401, 403))
