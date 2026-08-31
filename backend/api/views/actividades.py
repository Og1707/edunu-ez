from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from api.permissions import IsAdministrador, IsProfesor
from api.throttling import CompleteActivityRateThrottle
from api.models import Actividad, AsignacionActividad, Curso, EstudianteCurso, Usuario
from api.serializers import ActividadSerializer, EstudianteCursoSerializer
from api.services.actividades_service import ActividadesService
from api.services.cache_service import CacheService

# Decoradores comunes reutilizados en varias vistas
_JWT_AUTH = [JWTAuthentication, SessionAuthentication]
_IS_AUTH = [IsAuthenticated]
_IS_PROFESOR_O_ADMIN = [IsAuthenticated, IsProfesor | IsAdministrador]


@api_view(['GET', 'POST'])
@authentication_classes(_JWT_AUTH)
@permission_classes(_IS_AUTH)
def gestionar_actividades(request):
    """Listar y crear actividades."""
    if request.method == 'GET':
        usuario = request.user
        if usuario.rol == 'estudiante':
            return obtener_actividades_estudiante(request)
        if usuario.rol == 'profesor':
            return obtener_actividades_profesor(request)
        if usuario.rol == 'administrador':
            actividades = Actividad.objects.select_related('curso', 'creado_por').all().order_by('-fecha_creacion')
            serializer = ActividadSerializer(actividades, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'mensaje': 'Rol no reconocido'}, status=status.HTTP_403_FORBIDDEN)

    # POST — crear actividad
    usuario = request.user
    if usuario.rol not in ['profesor', 'administrador']:
        return Response(
            {'mensaje': 'No tienes permisos para crear actividades'},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = ActividadSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(creado_por=usuario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def obtener_tipos_actividad(request):
    """Obtener los tipos de actividad disponibles con caché Redis."""
    def _fetch_tipos():
        return [{'value': tipo[0], 'label': tipo[1]} for tipo in Actividad.TIPOS]

    tipos = CacheService.get_or_set(
        CacheService.KEY_TIPOS_ACTIVIDAD,
        _fetch_tipos,
        timeout=CacheService.TTL_CATALOGOS
    )
    return Response(tipos, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def obtener_actividades_profesor(request):
    """
    Obtiene todas las actividades de los cursos asignados a un profesor con estadísticas agregadas.
    Implementa consultas optimizadas sin N+1 a través de ActividadesService.
    """
    actividades_data = ActividadesService.obtener_actividades_profesor_optimizadas(request.user)
    return Response(actividades_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def asignar_actividad_curso(request):
    """Asignar una o varias actividades a un curso completo utilizando la capa de servicio."""
    curso_id = request.data.get('curso_id')
    actividad_id = request.data.get('actividad_id')
    actividad_ids = request.data.get('actividad_ids', [])

    if actividad_id:
        actividad_ids = [actividad_id]
    actividad_ids = [aid for aid in actividad_ids if aid]

    resultado = ActividadesService.asignar_actividad_a_curso(
        profesor=request.user,
        curso_id=curso_id,
        actividad_ids=actividad_ids
    )
    return Response(resultado, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def listar_estudiantes_curso(request):
    """Listar estudiantes de un curso específico optimizado con select_related."""
    curso_id = request.GET.get('curso_id')

    if not curso_id:
        return Response({'mensaje': 'Falta parámetro requerido: curso_id'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        curso = Curso.objects.get(id=curso_id)
        estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).select_related('estudiante')

        estudiantes_data = [
            {
                'id': ec.estudiante.id,
                'username': ec.estudiante.username,
                'nombre_completo': ec.estudiante.nombre_completo,
                'email': ec.estudiante.email,
                'fecha_inscripcion': ec.fecha_inscripcion,
            }
            for ec in estudiantes_curso
        ]

        return Response(
            {
                'curso': curso.nombre,
                'estudiantes': estudiantes_data,
                'total_estudiantes': len(estudiantes_data),
            },
            status=status.HTTP_200_OK,
        )

    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes(_IS_AUTH)
def actividades_asignadas_estudiante(request):
    """Obtener actividades asignadas al estudiante autenticado (optimizada anti N+1)."""
    estudiante = request.user

    if estudiante.rol != 'estudiante':
        return Response(
            {'mensaje': 'Este endpoint es solo para estudiantes'},
            status=status.HTTP_403_FORBIDDEN,
        )

    asignaciones = (
        AsignacionActividad.objects
        .filter(estudiante=estudiante)
        .select_related('actividad', 'actividad__curso', 'profesor')
        .order_by('-fecha_asignacion')
    )

    actividades_data = [
        {
            'asignacion_id': asignacion.id,
            'actividad_id': asignacion.actividad.id,
            'titulo': asignacion.actividad.titulo,
            'descripcion': asignacion.actividad.descripcion,
            'tipo': asignacion.actividad.tipo,
            'tipo_display': dict(asignacion.actividad.TIPOS).get(asignacion.actividad.tipo),
            'curso': asignacion.actividad.curso.nombre if asignacion.actividad.curso else None,
            'profesor': asignacion.profesor.nombre_completo if asignacion.profesor else None,
            'fecha_asignacion': asignacion.fecha_asignacion,
            'fecha_limite': asignacion.actividad.fecha_limite,
            'estado': asignacion.estado,
            'estado_display': dict(asignacion.ESTADOS_ASIGNACION).get(asignacion.estado),
            'calificacion': asignacion.calificacion,
            'comentarios_profesor': asignacion.comentarios_profesor,
            'tiene_entrega': bool(asignacion.archivo_entrega),
        }
        for asignacion in asignaciones
    ]

    return Response(
        {'actividades_asignadas': actividades_data, 'total_actividades': len(actividades_data)},
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def actividades_curso_profesor(request):
    """Obtener actividades de un curso para el profesor optimizado con agregaciones."""
    profesor = request.user
    curso_id = request.GET.get('curso_id')

    cursos = (
        Curso.objects.filter(id=curso_id, profesor=profesor)
        if curso_id
        else Curso.objects.filter(profesor=profesor)
    ).annotate(total_estudiantes_calc=Count('estudiantes', distinct=True))

    cursos_data = []
    for curso in cursos:
        actividades = (
            Actividad.objects
            .filter(curso=curso)
            .annotate(total_asignaciones_calc=Count('asignaciones', distinct=True))
            .order_by('-fecha_creacion')
        )
        total_estudiantes_curso = curso.total_estudiantes_calc

        actividades_data = []
        for actividad in actividades:
            total_asignaciones = actividad.total_asignaciones_calc
            porcentaje = (
                round((total_asignaciones / total_estudiantes_curso * 100), 1)
                if total_estudiantes_curso > 0 else 0
            )

            actividades_data.append({
                'id': actividad.id,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'tipo': actividad.tipo,
                'tipo_display': dict(actividad.TIPOS).get(actividad.tipo),
                'fecha_creacion': actividad.fecha_creacion,
                'fecha_limite': actividad.fecha_limite,
                'estado': actividad.estado,
                'asignaciones': {
                    'total_asignadas': total_asignaciones,
                    'total_estudiantes': total_estudiantes_curso,
                    'porcentaje_asignado': porcentaje,
                    'esta_asignada_completa': total_asignaciones == total_estudiantes_curso,
                },
            })

        cursos_data.append({
            'curso_id': curso.id,
            'curso_nombre': curso.nombre,
            'total_estudiantes': total_estudiantes_curso,
            'actividades': actividades_data,
            'total_actividades': len(actividades_data),
        })

    return Response(
        {'profesor': profesor.nombre_completo, 'cursos': cursos_data, 'total_cursos': len(cursos_data)},
        status=status.HTTP_200_OK,
    )


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes(_IS_AUTH)
def obtener_actividades_estudiante(request):
    """Obtener todas las actividades asignadas al estudiante autenticado."""
    usuario = request.user

    # Profesores/admins pueden consultar actividades de un estudiante por query param
    if usuario.rol in ['profesor', 'administrador']:
        target_id = request.GET.get('estudiante_id')
        if not target_id:
            return Response(
                {'mensaje': 'Parámetro estudiante_id requerido para consultar otro usuario'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            estudiante = Usuario.objects.get(id=target_id, rol='estudiante')
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    else:
        estudiante = usuario

    asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related(
        'actividad', 'actividad__curso', 'actividad__creado_por'
    )

    actividades_data = []
    for asignacion in asignaciones:
        actividad = asignacion.actividad
        actividad_data = ActividadSerializer(actividad).data
        actividad_data['progreso'] = {
            'completada': asignacion.estado in ['completada', 'revisada', 'calificada'],
            'fecha_completado': asignacion.fecha_entrega,
            'puntuacion': asignacion.calificacion,
            'estado': asignacion.estado,
            'comentarios': asignacion.comentarios_estudiante,
            'fecha_asignacion': asignacion.fecha_asignacion,
        }

        if actividad.fecha_limite:
            ahora = timezone.now().date()
            if actividad.fecha_limite < ahora:
                actividad_data['estado_tiempo'] = 'vencida'
            elif (actividad.fecha_limite - ahora).days <= 3:
                actividad_data['estado_tiempo'] = 'por_vencer'
            else:
                actividad_data['estado_tiempo'] = 'activa'
        else:
            actividad_data['estado_tiempo'] = 'sin_limite'

        actividades_data.append(actividad_data)

    return Response(actividades_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes(_JWT_AUTH)
@permission_classes(_IS_AUTH)
def iniciar_actividad_estudiante(request):
    """Marcar que un estudiante ha iniciado una actividad."""
    actividad_id = request.data.get('actividad_id')
    resultado = ActividadesService.iniciar_actividad(
        estudiante=request.user,
        actividad_id=actividad_id
    )
    return Response(resultado, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes(_JWT_AUTH)
@permission_classes(_IS_AUTH)
@throttle_classes([CompleteActivityRateThrottle])
def completar_actividad_estudiante(request):
    """Marcar una actividad como completada por el estudiante con rate limiting."""
    actividad_id = request.data.get('actividad_id')
    puntuacion = request.data.get('puntuacion', 0)
    tiempo_empleado = request.data.get('tiempo_empleado', 0)
    respuestas_detalle = request.data.get('respuestas_detalle', [])

    resultado = ActividadesService.completar_actividad(
        estudiante=request.user,
        actividad_id=actividad_id,
        puntuacion=puntuacion,
        tiempo_empleado=tiempo_empleado,
        respuestas_detalle=respuestas_detalle
    )
    return Response(resultado, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes(_IS_AUTH)
def obtener_estadisticas_estudiante(request):
    """Obtener estadísticas de progreso del estudiante autenticado."""
    usuario = request.user

    if usuario.rol in ['profesor', 'administrador']:
        target_id = request.GET.get('estudiante_id')
        if not target_id:
            return Response(
                {'mensaje': 'Parámetro estudiante_id requerido para consultar otro usuario'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            estudiante = Usuario.objects.get(id=target_id, rol='estudiante')
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    else:
        estudiante = usuario

    asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related('actividad')

    total_actividades = asignaciones.count()
    actividades_completadas = asignaciones.filter(estado__in=['completada', 'revisada', 'calificada']).count()
    actividades_pendientes = total_actividades - actividades_completadas

    ahora = timezone.now().date()
    fecha_limite_pronto = ahora + timezone.timedelta(days=7)

    actividades_por_vencer = asignaciones.filter(
        actividad__fecha_limite__lte=fecha_limite_pronto,
        actividad__fecha_limite__gte=ahora,
        estado__in=['asignada', 'en_progreso'],
    ).count()

    actividades_vencidas = asignaciones.filter(
        actividad__fecha_limite__lt=ahora,
        estado__in=['asignada', 'en_progreso'],
    ).count()

    puntuacion_promedio = (
        asignaciones.filter(
            estado__in=['completada', 'revisada', 'calificada'],
            calificacion__isnull=False,
        ).aggregate(promedio=Avg('calificacion'))['promedio'] or 0
    )

    return Response(
        {
            'actividades_completadas': actividades_completadas,
            'actividades_pendientes': actividades_pendientes,
            'actividades_por_vencer': actividades_por_vencer,
            'actividades_vencidas': actividades_vencidas,
            'puntuacion_promedio': round(puntuacion_promedio, 2),
            'porcentaje_completado': round(
                (actividades_completadas / total_actividades * 100) if total_actividades > 0 else 0, 2
            ),
        },
        status=status.HTTP_200_OK,
    )


@api_view(['PUT', 'DELETE'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def gestionar_actividad_especifica(request, actividad_id):
    """Editar o eliminar actividad."""
    try:
        actividad = Actividad.objects.select_related('curso').get(id=actividad_id)

        if request.user.rol == 'profesor' and actividad.curso and actividad.curso.profesor != request.user:
            return Response(
                {'mensaje': 'Solo puedes gestionar actividades de tus cursos'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if request.method == 'PUT':
            serializer = ActividadSerializer(actividad, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        actividad.delete()
        return Response({'mensaje': 'Actividad eliminada exitosamente'}, status=status.HTTP_200_OK)

    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def agregar_estudiante_a_curso(request):
    """Agregar estudiante a un curso."""
    estudiante_id = request.data.get('estudiante_id')
    curso_id = request.data.get('curso_id')

    inscripcion = ActividadesService.inscribir_estudiante_curso(
        user_solicitante=request.user,
        curso_id=curso_id,
        estudiante_id=estudiante_id
    )
    serializer = EstudianteCursoSerializer(inscripcion)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def remover_estudiante_de_curso(request, inscripcion_id):
    """Remover estudiante de un curso."""
    ActividadesService.remover_estudiante_curso(
        user_solicitante=request.user,
        inscripcion_id=inscripcion_id
    )
    return Response({'mensaje': 'Estudiante removido del curso exitosamente'}, status=status.HTTP_200_OK)
