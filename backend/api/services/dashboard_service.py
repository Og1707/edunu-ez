"""Consultas agregadas y autorización de lectura para el dashboard del personal."""

from collections import defaultdict
from decimal import Decimal

from django.db.models import Count, Prefetch

from api.exceptions import PermissionDeniedBusinessException, ResourceNotFoundException
from api.models import Actividad, AsignacionActividad, Curso, EstudianteCurso, Usuario


class DashboardService:
    """Construye un resumen acotado al rol del usuario autenticado."""

    COMPLETED_STATES = ('completada', 'revisada', 'calificada')

    @classmethod
    def _scope(cls, user):
        if user.rol == 'administrador':
            courses = Curso.objects.all()
            students = Usuario.objects.filter(rol='estudiante')
        elif user.rol == 'profesor':
            courses = Curso.objects.filter(profesor=user)
            students = Usuario.objects.filter(
                rol='estudiante', cursos__curso__profesor=user
            ).distinct()
        else:
            raise PermissionDeniedBusinessException(
                'El dashboard está disponible para administradores y profesores.',
                code='ROL_NO_PERMITIDO',
            )

        return courses, students

    @staticmethod
    def _average(values):
        grades = [Decimal(value) for value in values if value is not None]
        return round(float(sum(grades) / len(grades)), 2) if grades else None

    @classmethod
    def _assignment_rows(cls, courses, students):
        return list(
            AsignacionActividad.objects.filter(
                actividad__curso__in=courses,
                estudiante__in=students,
            ).select_related('actividad', 'actividad__curso', 'actividad__curso__ciencias_naturales__materia', 'estudiante')
            .order_by('fecha_asignacion', 'id')
        )

    @classmethod
    def get_summary(cls, user):
        courses, students = cls._scope(user)
        course_rows = list(courses.select_related(
            'profesor', 'ciencias_naturales__materia'
        ).annotate(
            total_estudiantes=Count('estudiantes__estudiante', distinct=True),
            total_actividades=Count('actividades', distinct=True),
        ).prefetch_related(Prefetch('actividades', queryset=Actividad.objects.order_by('-fecha_creacion'))).order_by('nombre'))
        course_ids = [course.id for course in course_rows]
        scoped_students = (
            students if user.rol == 'administrador'
            else students.filter(cursos__curso_id__in=course_ids).distinct()
        )
        assignments = cls._assignment_rows(courses, scoped_students)

        by_course = defaultdict(list)
        by_student = defaultdict(list)
        by_subject = defaultdict(list)
        by_activity = defaultdict(list)
        for assignment in assignments:
            course_id = assignment.actividad.curso_id
            by_course[course_id].append(assignment)
            by_student[assignment.estudiante_id].append(assignment)
            by_activity[assignment.actividad_id].append(assignment)
            try:
                subject = assignment.actividad.curso.ciencias_naturales.materia
            except (AttributeError, type(assignment.actividad.curso).DoesNotExist):
                subject = None
            if subject and assignment.calificacion is not None:
                by_subject[subject.id].append((subject, assignment.calificacion))

        course_data = []
        for course in course_rows:
            course_assignments = by_course[course.id]
            completed = [row for row in course_assignments if row.estado in cls.COMPLETED_STATES]
            try:
                subject = course.ciencias_naturales.materia
                subject_data = {'id': subject.id, 'nombre': subject.nombre}
            except AttributeError:
                subject_data = None
            course_data.append({
                'id': course.id,
                'nombre': course.nombre,
                'descripcion': course.descripcion,
                'profesor_id': course.profesor_id,
                'profesor_nombre': course.profesor.nombre_completo if course.profesor else None,
                'total_estudiantes': course.total_estudiantes,
                'total_actividades': course.total_actividades,
                'asignaciones': len(course_assignments),
                'completadas': len(completed),
                'promedio': cls._average(row.calificacion for row in completed),
                'materia': subject_data,
            })

        student_data = []
        for student in scoped_students.order_by('nombre_completo', 'username'):
            rows = by_student[student.id]
            graded = [row for row in rows if row.estado in cls.COMPLETED_STATES and row.calificacion is not None]
            course_names = list(EstudianteCurso.objects.filter(
                estudiante=student, curso_id__in=course_ids
            ).order_by('curso__nombre').values_list('curso__nombre', flat=True))
            trend = [float(row.calificacion) for row in graded]
            student_data.append({
                'id': student.id,
                'nombre': student.nombre_completo or student.username,
                'username': student.username,
                'cursos': course_names,
                'actividades_completadas': sum(row.estado in cls.COMPLETED_STATES for row in rows),
                'actividades_totales': len(rows),
                'promedio': cls._average(row.calificacion for row in graded),
                'tendencia': trend[-8:],
            })

        subject_data = []
        for subject_id, values in by_subject.items():
            subject = values[0][0]
            subject_data.append({
                'id': subject_id,
                'nombre': subject.nombre,
                'promedio': cls._average(value for _, value in values),
                'resultados': len(values),
            })

        activities = []
        for course in course_rows:
            for activity in course.actividades.all():
                rows = by_activity[activity.id]
                activities.append({
                    'id': activity.id,
                    'titulo': activity.titulo,
                    'curso': course.nombre,
                    'estado': activity.estado,
                    'asignaciones': len(rows),
                    'completadas': sum(row.estado in cls.COMPLETED_STATES for row in rows),
                    'promedio': cls._average(
                        row.calificacion for row in rows
                        if row.estado in cls.COMPLETED_STATES
                    ),
                })

        graded_assignments = [
            row for row in assignments
            if row.estado in cls.COMPLETED_STATES and row.calificacion is not None
        ]
        kpis = {
            'cursos': len(course_rows),
            'estudiantes': scoped_students.count(),
            'profesores': Usuario.objects.filter(rol='profesor').count() if user.rol == 'administrador' else None,
            'actividades': sum(course.actividades.count() for course in course_rows),
            'promedio': cls._average(row.calificacion for row in graded_assignments),
            'completadas': len(graded_assignments),
        }
        return {
            'rol': user.rol,
            'kpis': kpis,
            'cursos': course_data,
            'estudiantes': student_data,
            'asignaturas': subject_data,
            'actividades': activities,
        }

    @classmethod
    def get_student_detail(cls, user, student_id):
        courses, students = cls._scope(user)
        try:
            student = students.get(pk=student_id)
        except Usuario.DoesNotExist:
            # 404 evita revelar si un estudiante ajeno existe.
            raise ResourceNotFoundException('Estudiante no encontrado.', code='ESTUDIANTE_NO_ENCONTRADO')

        course_ids = list(courses.values_list('id', flat=True))
        enrollments = EstudianteCurso.objects.filter(
            estudiante=student, curso_id__in=course_ids
        ).select_related('curso').order_by('curso__nombre')
        rows = cls._assignment_rows(courses, Usuario.objects.filter(pk=student.pk))
        history = [{
            'id': row.id,
            'actividad': row.actividad.titulo,
            'curso': row.actividad.curso.nombre,
            'estado': row.estado,
            'calificacion': float(row.calificacion) if row.calificacion is not None else None,
            'fecha': row.fecha_entrega.isoformat() if row.fecha_entrega else row.fecha_asignacion.isoformat(),
        } for row in rows]
        graded = [row.calificacion for row in rows if row.estado in cls.COMPLETED_STATES and row.calificacion is not None]
        return {
            'id': student.id,
            'nombre': student.nombre_completo or student.username,
            'username': student.username,
            'cursos': [enrollment.curso.nombre for enrollment in enrollments],
            'promedio': cls._average(graded),
            'historial': history,
        }
