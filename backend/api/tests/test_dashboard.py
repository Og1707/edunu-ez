from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Actividad, AsignacionActividad, Asignatura, Curso, EstudianteCurso, Usuario


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

    def test_estudiante_detalle_incluye_materias_con_kpis(self):
        math, _ = Asignatura.objects.get_or_create(nombre='Matemáticas')
        lang, _ = Asignatura.objects.get_or_create(nombre='Lenguaje')
        self.course.asignaturas.add(math, lang)

        # Actividad de matemáticas calificada
        act_math = Actividad.objects.create(
            titulo='Álgebra', curso=self.course, asignatura=math, creado_por=self.teacher
        )
        AsignacionActividad.objects.create(
            actividad=act_math, estudiante=self.student, profesor=self.teacher,
            estado='calificada', calificacion=90.0,
        )

        # Actividad de lenguaje con 2 notas
        act_lang1 = Actividad.objects.create(
            titulo='Lectura 1', curso=self.course, asignatura=lang, creado_por=self.teacher
        )
        act_lang2 = Actividad.objects.create(
            titulo='Lectura 2', curso=self.course, asignatura=lang, creado_por=self.teacher
        )
        AsignacionActividad.objects.create(
            actividad=act_lang1, estudiante=self.student, profesor=self.teacher,
            estado='calificada', calificacion=92.0,
        )
        AsignacionActividad.objects.create(
            actividad=act_lang2, estudiante=self.student, profesor=self.teacher,
            estado='completada', calificacion=88.0,
        )

        self.client.force_authenticate(self.teacher)
        detail = self.client.get(f'/api/dashboard/estudiantes/{self.student.id}/')
        self.assertEqual(detail.status_code, 200)

        materias = detail.data['materias']
        self.assertEqual(len(materias), 2)

        lang_kpi = next(m for m in materias if m['nombre'] == 'Lenguaje')
        self.assertEqual(lang_kpi['promedio'], 90.0)
        self.assertEqual(lang_kpi['total_actividades'], 2)
        self.assertEqual(lang_kpi['actividades_completadas'], 2)

        math_kpi = next(m for m in materias if m['nombre'] == 'Matemáticas')
        self.assertEqual(math_kpi['promedio'], 90.0)
        self.assertEqual(math_kpi['total_actividades'], 1)
        self.assertEqual(math_kpi['actividades_completadas'], 1)

    def test_materia_inscrita_sin_calificaciones_devuelve_promedio_null(self):
        science, _ = Asignatura.objects.get_or_create(nombre='Ciencias Naturales')
        self.course.asignaturas.add(science)

        self.client.force_authenticate(self.teacher)
        detail = self.client.get(f'/api/dashboard/estudiantes/{self.student.id}/')
        self.assertEqual(detail.status_code, 200)

        science_kpi = next(m for m in detail.data['materias'] if m['nombre'] == 'Ciencias Naturales')
        self.assertIsNone(science_kpi['promedio'])
        self.assertEqual(science_kpi['total_actividades'], 0)
        self.assertEqual(science_kpi['actividades_completadas'], 0)

    def test_actividades_pendientes_no_se_computan_como_cero(self):
        english, _ = Asignatura.objects.get_or_create(nombre='Inglés')
        self.course.asignaturas.add(english)

        act_pending = Actividad.objects.create(
            titulo='Reading test', curso=self.course, asignatura=english, creado_por=self.teacher
        )
        AsignacionActividad.objects.create(
            actividad=act_pending, estudiante=self.student, profesor=self.teacher,
            estado='asignada', calificacion=None,
        )

        self.client.force_authenticate(self.teacher)
        detail = self.client.get(f'/api/dashboard/estudiantes/{self.student.id}/')
        self.assertEqual(detail.status_code, 200)

        eng_kpi = next(m for m in detail.data['materias'] if m['nombre'] == 'Inglés')
        self.assertIsNone(eng_kpi['promedio'])
        self.assertEqual(eng_kpi['total_actividades'], 1)
        self.assertEqual(eng_kpi['actividades_completadas'], 0)

    def test_estudiante_sin_materias_inscritas_devuelve_lista_vacia(self):
        self.client.force_authenticate(self.teacher)
        detail = self.client.get(f'/api/dashboard/estudiantes/{self.student.id}/')
        self.assertEqual(detail.status_code, 200)
        # self.course originalmente no tiene asignaturas asociadas
        self.assertEqual(detail.data['materias'], [])

