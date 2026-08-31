"""
Servicio de negocio para la gestión de actividades y asignaciones.
Encapsula transacciones atómicas, validaciones de permisos y optimización de consultas.
"""

import logging
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone

from api.models import Actividad, AsignacionActividad, Curso, EstudianteCurso, Usuario
from api.exceptions import (
    ResourceNotFoundException,
    PermissionDeniedBusinessException,
    BusinessValidationException,
    ConflictBusinessException
)
from api.services.n8n_service import enviar_resultado_actividad_async, registrar_evento_actividad

logger = logging.getLogger(__name__)


class ActividadesService:
    """
    Capa de servicio pura para la gestión del ciclo de vida de actividades educativas.
    """

    @classmethod
    def obtener_actividades_profesor_optimizadas(cls, profesor: Usuario) -> List[Dict[str, Any]]:
        """
        Obtiene las actividades de los cursos de un profesor con estadísticas agregadas en 1 sola consulta
        eliminando el problema de consultas N+1.
        """
        cursos_profesor = Curso.objects.filter(profesor=profesor)
        if not cursos_profesor.exists():
            return []

        # Consulta optimizada con select_related y agregaciones condicionales
        actividades = (
            Actividad.objects
            .filter(curso__in=cursos_profesor)
            .select_related('curso', 'creado_por')
            .annotate(
                total_asignaciones_calc=Count('asignaciones', distinct=True),
                completadas_calc=Count(
                    'asignaciones',
                    filter=Q(asignaciones__estado__in=['completada', 'revisada', 'calificada']),
                    distinct=True
                ),
                pendientes_calc=Count(
                    'asignaciones',
                    filter=Q(asignaciones__estado='asignada'),
                    distinct=True
                ),
                en_progreso_calc=Count(
                    'asignaciones',
                    filter=Q(asignaciones__estado='en_progreso'),
                    distinct=True
                ),
                estudiantes_curso_calc=Count('curso__estudiantes', distinct=True)
            )
            .order_by('-fecha_creacion')
        )

        resultado = []
        for act in actividades:
            estudiantes_count = act.estudiantes_curso_calc
            asignaciones_count = act.total_asignaciones_calc
            porcentaje = (
                round((asignaciones_count / estudiantes_count * 100), 1)
                if estudiantes_count > 0 else 0
            )

            resultado.append({
                'id': act.id,
                'titulo': act.titulo,
                'descripcion': act.descripcion,
                'tipo': act.tipo,
                'template_type': act.template_type,
                'recurso': act.recurso,
                'fecha_limite': act.fecha_limite,
                'estado': act.estado,
                'curso': act.curso_id,
                'curso_nombre': act.curso.nombre if act.curso else None,
                'creado_por': act.creado_por_id,
                'fecha_creacion': act.fecha_creacion,
                'estadisticas': {
                    'total_estudiantes': estudiantes_count,
                    'total_asignaciones': asignaciones_count,
                    'completadas': act.completadas_calc,
                    'pendientes': act.pendientes_calc,
                    'en_progreso': act.en_progreso_calc,
                    'porcentaje_asignado': porcentaje,
                }
            })

        return resultado

    @classmethod
    @transaction.atomic
    def asignar_actividad_a_curso(
        cls, profesor: Usuario, curso_id: int, actividad_ids: List[int]
    ) -> Dict[str, Any]:
        """
        Asigna una o más actividades a todos los estudiantes inscritos en un curso de manera atómica.
        """
        if not curso_id or not actividad_ids:
            raise BusinessValidationException(
                "Faltan datos requeridos: curso_id y al menos una actividad.",
                code="DATOS_INCOMPLETOS"
            )

        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            raise ResourceNotFoundException("El curso especificado no existe.", code="CURSO_NO_ENCONTRADO")

        if profesor.rol == 'profesor' and curso.profesor != profesor:
            raise PermissionDeniedBusinessException(
                "Solo puedes asignar actividades en cursos que diriges.",
                code="CURSO_NO_AUTORIZADO"
            )

        estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).select_related('estudiante')
        if not estudiantes_curso.exists():
            raise BusinessValidationException(
                "No hay estudiantes inscritos en este curso.",
                code="CURSO_SIN_ESTUDIANTES"
            )

        actividades = Actividad.objects.filter(id__in=actividad_ids, curso=curso)
        if not actividades.exists():
            raise ResourceNotFoundException(
                "No se encontraron actividades válidas pertenecientes a este curso.",
                code="ACTIVIDADES_NO_VALIDAS"
            )

        asignaciones_creadas = []
        asignaciones_existentes = []

        for actividad in actividades:
            for ec in estudiantes_curso:
                estudiante = ec.estudiante
                asignacion, created = AsignacionActividad.objects.get_or_create(
                    actividad=actividad,
                    estudiante=estudiante,
                    defaults={'profesor': profesor, 'estado': 'asignada'}
                )
                entry = {
                    'estudiante_id': estudiante.id,
                    'estudiante': estudiante.username,
                    'estudiante_nombre': estudiante.nombre_completo,
                    'email': estudiante.email,
                }
                if created:
                    asignaciones_creadas.append(entry)
                else:
                    asignaciones_existentes.append({**entry, 'estado_actual': asignacion.estado})

        return {
            'mensaje': 'Actividad asignada al curso exitosamente',
            'curso': curso.nombre,
            'nuevas_asignaciones': asignaciones_creadas,
            'asignaciones_existentes': asignaciones_existentes,
            'resumen': {
                'total_estudiantes': len(estudiantes_curso),
                'nuevas_asignaciones': len(asignaciones_creadas),
                'ya_asignadas': len(asignaciones_existentes),
            }
        }

    @classmethod
    @transaction.atomic
    def iniciar_actividad(cls, estudiante: Usuario, actividad_id: int) -> Dict[str, Any]:
        """
        Marca el inicio de una actividad para un estudiante y actualiza su estado.
        """
        if not actividad_id:
            raise BusinessValidationException("Falta el identificador de la actividad.", code="ACTIVIDAD_ID_FALTANTE")

        if estudiante.rol != 'estudiante':
            raise PermissionDeniedBusinessException(
                "Solo los estudiantes pueden iniciar actividades.",
                code="ROL_NO_PERMITIDO"
            )

        try:
            actividad = Actividad.objects.select_related('curso', 'creado_por').get(id=actividad_id)
        except Actividad.DoesNotExist:
            raise ResourceNotFoundException("Actividad no encontrada.", code="ACTIVIDAD_NO_ENCONTRADA")

        if not EstudianteCurso.objects.filter(estudiante=estudiante, curso=actividad.curso).exists():
            raise PermissionDeniedBusinessException(
                "No tienes acceso a esta actividad porque no estás inscrito en el curso.",
                code="ACCESO_DENEGADO_CURSO"
            )

        asignacion, created = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': actividad.creado_por or (actividad.curso.profesor if actividad.curso else None),
                'estado': 'en_progreso',
            }
        )

        if not created and asignacion.estado == 'asignada':
            asignacion.estado = 'en_progreso'
            asignacion.save(update_fields=['estado'])

        return {
            'mensaje': 'Actividad iniciada exitosamente',
            'progreso': {
                'estado': asignacion.estado,
                'fecha_asignacion': asignacion.fecha_asignacion,
            }
        }

    @classmethod
    @transaction.atomic
    def completar_actividad(
        cls,
        estudiante: Usuario,
        actividad_id: int,
        puntuacion: float = 0,
        tiempo_empleado: int = 0,
        respuestas_detalle: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Completa una actividad, calcula tardanza, actualiza la base de datos y despacha el webhook a n8n.
        """
        if not actividad_id:
            raise BusinessValidationException("Falta el identificador de la actividad.", code="ACTIVIDAD_ID_FALTANTE")

        if estudiante.rol != 'estudiante':
            raise PermissionDeniedBusinessException(
                "Solo los estudiantes pueden completar actividades.",
                code="ROL_NO_PERMITIDO"
            )

        try:
            actividad = Actividad.objects.select_related('curso', 'creado_por').get(id=actividad_id)
        except Actividad.DoesNotExist:
            raise ResourceNotFoundException("Actividad no encontrada.", code="ACTIVIDAD_NO_ENCONTRADA")

        if not EstudianteCurso.objects.filter(estudiante=estudiante, curso=actividad.curso).exists():
            raise PermissionDeniedBusinessException(
                "No tienes acceso a esta actividad porque no estás inscrito en el curso.",
                code="ACCESO_DENEGADO_CURSO"
            )

        es_tardia = bool(actividad.fecha_limite and actividad.fecha_limite < timezone.now().date())

        asignacion, _ = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': actividad.creado_por or (actividad.curso.profesor if actividad.curso else None),
                'estado': 'completada',
            }
        )

        asignacion.estado = 'completada'
        asignacion.fecha_entrega = timezone.now()
        asignacion.calificacion = puntuacion
        asignacion.comentarios_estudiante = (
            f'Entregada tarde. Tiempo empleado: {tiempo_empleado} minutos'
            if es_tardia
            else f'Tiempo empleado: {tiempo_empleado} minutos'
        )
        asignacion.save()

        # Registro de auditoría
        registrar_evento_actividad(
            actividad_id=actividad_id,
            estudiante_id=estudiante.id,
            evento_tipo='completada',
            datos_adicionales={
                'puntuacion': puntuacion,
                'tiempo_empleado': tiempo_empleado,
                'es_tardia': es_tardia,
            }
        )

        # Despacho no-bloqueante a n8n
        enviar_resultado_actividad_async({
            'estudiante_id': estudiante.id,
            'estudiante_nombre': estudiante.nombre_completo,
            'estudiante_email': estudiante.email,
            'actividad_id': actividad.id,
            'actividad_titulo': actividad.titulo,
            'actividad_tipo': actividad.tipo,
            'curso_id': actividad.curso.id if actividad.curso else None,
            'curso_nombre': actividad.curso.nombre if actividad.curso else None,
            'puntuacion': puntuacion,
            'tiempo_empleado': tiempo_empleado,
            'fecha_entrega': asignacion.fecha_entrega,
            'estado': asignacion.estado,
            'es_tardia': es_tardia,
            'respuestas_detalle': respuestas_detalle or [],
        })

        return {
            'mensaje': 'Actividad completada exitosamente',
            'progreso': {
                'completada': True,
                'fecha_completado': asignacion.fecha_entrega,
                'puntuacion': asignacion.calificacion,
                'tiempo_empleado': tiempo_empleado,
                'es_tardia': es_tardia,
                'estado': asignacion.estado,
            }
        }

    @classmethod
    @transaction.atomic
    def inscribir_estudiante_curso(cls, user_solicitante: Usuario, curso_id: int, estudiante_id: int) -> EstudianteCurso:
        """Inscribe a un estudiante en un curso."""
        if not estudiante_id or not curso_id:
            raise BusinessValidationException("Faltan datos requeridos (estudiante_id o curso_id).", code="DATOS_FALTANTES")

        try:
            estudiante = Usuario.objects.get(id=estudiante_id, rol='estudiante')
            curso = Curso.objects.get(id=curso_id)
        except Usuario.DoesNotExist:
            raise ResourceNotFoundException("Estudiante no encontrado.", code="ESTUDIANTE_NO_ENCONTRADO")
        except Curso.DoesNotExist:
            raise ResourceNotFoundException("Curso no encontrado.", code="CURSO_NO_ENCONTRADO")

        if user_solicitante.rol == 'profesor' and curso.profesor != user_solicitante:
            raise PermissionDeniedBusinessException(
                "Solo puedes agregar estudiantes a tus propios cursos.",
                code="NO_AUTORIZADO"
            )

        if EstudianteCurso.objects.filter(estudiante=estudiante, curso=curso).exists():
            raise ConflictBusinessException("El estudiante ya está inscrito en este curso.", code="YA_INSCRITO")

        return EstudianteCurso.objects.create(estudiante=estudiante, curso=curso)

    @classmethod
    @transaction.atomic
    def remover_estudiante_curso(cls, user_solicitante: Usuario, inscripcion_id: int) -> None:
        """Remueve a un estudiante de un curso."""
        try:
            inscripcion = EstudianteCurso.objects.select_related('curso').get(id=inscripcion_id)
        except EstudianteCurso.DoesNotExist:
            raise ResourceNotFoundException("Inscripción no encontrada.", code="INSCRIPCION_NO_ENCONTRADA")

        if user_solicitante.rol == 'profesor' and inscripcion.curso.profesor != user_solicitante:
            raise PermissionDeniedBusinessException(
                "Solo puedes remover estudiantes de tus propios cursos.",
                code="NO_AUTORIZADO"
            )

        inscripcion.delete()
