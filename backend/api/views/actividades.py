from django.db.models import Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from api.permissions import IsAdministrador, IsProfesor
from ..models import Actividad, AsignacionActividad, Curso, EstudianteCurso, Usuario
from ..serializers import ActividadSerializer, EstudianteCursoSerializer
from ..webhooks import enviar_resultado_actividad_n8n_async, registrar_evento_actividad

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
            actividades = Actividad.objects.all().order_by('-fecha_creacion')
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
    """Obtener los tipos de actividad disponibles."""
    tipos = [{'value': tipo[0], 'label': tipo[1]} for tipo in Actividad.TIPOS]
    return Response(tipos, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def obtener_actividades_profesor(request):
    """
    Obtiene todas las actividades de los cursos asignados a un profesor.

    Comportamiento:
        - Si el profesor tiene cursos: retorna lista de actividades con estadísticas
        - Si el profesor NO tiene cursos: retorna array vacío con Status 200

    Estadísticas por actividad:
        - total_estudiantes: Estudiantes inscritos en el curso
        - total_asignaciones: Veces que se asignó la actividad
        - completadas: Asignaciones con estado final
        - pendientes: Asignaciones en estado 'asignada'
        - en_progreso: Asignaciones activas
        - porcentaje_asignado: % de estudiantes a los que se asignó

    Returns:
        Response: JSON array de actividades con estadísticas
        - Status 200: Éxito (incluso con lista vacía)
        - Status 401: No autenticado
        - Status 403: Rol insuficiente
    """
    profesor = request.user
    cursos_profesor = Curso.objects.filter(profesor=profesor)

    if not cursos_profesor.exists():
        return Response([], status=status.HTTP_200_OK)

    actividades_data = []
    for actividad in Actividad.objects.filter(curso__in=cursos_profesor).order_by('-fecha_creacion'):
        asignaciones = AsignacionActividad.objects.filter(actividad=actividad)
        estudiantes_curso = EstudianteCurso.objects.filter(curso=actividad.curso).count()

        actividad_data = ActividadSerializer(actividad).data
        actividad_data['estadisticas'] = {
            'total_estudiantes': estudiantes_curso,
            'total_asignaciones': asignaciones.count(),
            'completadas': asignaciones.filter(estado__in=['completada', 'revisada', 'calificada']).count(),
            'pendientes': asignaciones.filter(estado='asignada').count(),
            'en_progreso': asignaciones.filter(estado='en_progreso').count(),
            'porcentaje_asignado': round(
                (asignaciones.count() / estudiantes_curso * 100) if estudiantes_curso > 0 else 0, 1
            ),
        }
        actividades_data.append(actividad_data)

    return Response(actividades_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def asignar_actividad_curso(request):
    """Asignar una o varias actividades a un curso completo."""
    profesor = request.user
    curso_id = request.data.get('curso_id')
    actividad_id = request.data.get('actividad_id')
    actividad_ids = request.data.get('actividad_ids', [])

    if actividad_id:
        actividad_ids = [actividad_id]
    actividad_ids = [aid for aid in actividad_ids if aid]

    if not curso_id or not actividad_ids:
        return Response(
            {'mensaje': 'Faltan datos requeridos: curso_id y al menos una actividad'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        curso = Curso.objects.get(id=curso_id)

        if profesor.rol == 'profesor' and curso.profesor != profesor:
            return Response(
                {'mensaje': 'Solo puedes asignar actividades en cursos que diriges'},
                status=status.HTTP_403_FORBIDDEN,
            )

        estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).select_related('estudiante')
        if not estudiantes_curso.exists():
            return Response(
                {'mensaje': 'No hay estudiantes inscritos en este curso'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        asignaciones_creadas = []
        asignaciones_existentes = []
        errores = []
        actividades_procesadas = []

        for aid in actividad_ids:
            try:
                actividad = Actividad.objects.get(id=aid, curso=curso)
                actividades_procesadas.append(actividad)
            except Actividad.DoesNotExist:
                errores.append(f'Actividad {aid} no encontrada o no pertenece al curso {curso.nombre}')

        if not actividades_procesadas:
            return Response(
                {'mensaje': 'No se encontraron actividades válidas para asignar', 'errores': errores},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for actividad in actividades_procesadas:
            for estudiante_curso in estudiantes_curso:
                estudiante = estudiante_curso.estudiante
                asignacion, created = AsignacionActividad.objects.get_or_create(
                    actividad=actividad,
                    estudiante=estudiante,
                    defaults={'profesor': profesor, 'estado': 'asignada'},
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

        return Response(
            {
                'mensaje': 'Actividad asignada al curso exitosamente',
                'curso': curso.nombre,
                'nuevas_asignaciones': asignaciones_creadas,
                'asignaciones_existentes': asignaciones_existentes,
                'resumen': {
                    'total_estudiantes': len(estudiantes_curso),
                    'nuevas_asignaciones': len(asignaciones_creadas),
                    'ya_asignadas': len(asignaciones_existentes),
                    'errores': len(errores),
                },
                'errores': errores,
            },
            status=status.HTTP_201_CREATED,
        )

    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def listar_estudiantes_curso(request):
    """Listar estudiantes de un curso específico."""
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
    """Obtener actividades asignadas al estudiante autenticado."""
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
            'curso': asignacion.actividad.curso.nombre,
            'profesor': asignacion.profesor.nombre_completo,
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
    """Obtener actividades de un curso para el profesor."""
    profesor = request.user
    curso_id = request.GET.get('curso_id')

    cursos = (
        Curso.objects.filter(id=curso_id, profesor=profesor)
        if curso_id
        else Curso.objects.filter(profesor=profesor)
    )

    cursos_data = []
    for curso in cursos:
        actividades = Actividad.objects.filter(curso=curso).order_by('-fecha_creacion')
        actividades_data = []
        for actividad in actividades:
            total_asignaciones = AsignacionActividad.objects.filter(actividad=actividad).count()
            total_estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).count()

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
                    'porcentaje_asignado': round(
                        (total_asignaciones / total_estudiantes_curso * 100)
                        if total_estudiantes_curso > 0 else 0,
                        1,
                    ),
                    'esta_asignada_completa': total_asignaciones == total_estudiantes_curso,
                },
            })

        cursos_data.append({
            'curso_id': curso.id,
            'curso_nombre': curso.nombre,
            'total_estudiantes': EstudianteCurso.objects.filter(curso=curso).count(),
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
        'actividad', 'actividad__curso'
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
    estudiante = request.user

    if not actividad_id:
        return Response({'mensaje': 'Falta actividad_id'}, status=status.HTTP_400_BAD_REQUEST)

    if estudiante.rol != 'estudiante':
        return Response({'mensaje': 'Solo los estudiantes pueden iniciar actividades'}, status=status.HTTP_403_FORBIDDEN)

    try:
        actividad = Actividad.objects.get(id=actividad_id)

        if not EstudianteCurso.objects.filter(estudiante=estudiante, curso=actividad.curso).exists():
            return Response({'mensaje': 'No tienes acceso a esta actividad'}, status=status.HTTP_403_FORBIDDEN)

        asignacion, created = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': actividad.creado_por or actividad.curso.profesor,
                'estado': 'en_progreso',
            },
        )

        if not created and asignacion.estado == 'asignada':
            asignacion.estado = 'en_progreso'
            asignacion.save()

        return Response(
            {
                'mensaje': 'Actividad iniciada exitosamente',
                'progreso': {
                    'estado': asignacion.estado,
                    'fecha_asignacion': asignacion.fecha_asignacion,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes(_JWT_AUTH)
@permission_classes(_IS_AUTH)
def completar_actividad_estudiante(request):
    """Marcar una actividad como completada por el estudiante."""
    actividad_id = request.data.get('actividad_id')
    puntuacion = request.data.get('puntuacion', 0)
    tiempo_empleado = request.data.get('tiempo_empleado', 0)
    respuestas_detalle = request.data.get('respuestas_detalle', [])
    estudiante = request.user

    if not actividad_id:
        return Response({'mensaje': 'Falta actividad_id'}, status=status.HTTP_400_BAD_REQUEST)

    if estudiante.rol != 'estudiante':
        return Response({'mensaje': 'Solo los estudiantes pueden completar actividades'}, status=status.HTTP_403_FORBIDDEN)

    try:
        actividad = Actividad.objects.get(id=actividad_id)

        if not EstudianteCurso.objects.filter(estudiante=estudiante, curso=actividad.curso).exists():
            return Response({'mensaje': 'No tienes acceso a esta actividad'}, status=status.HTTP_403_FORBIDDEN)

        es_tardia = bool(actividad.fecha_limite and actividad.fecha_limite < timezone.now().date())

        asignacion, _ = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': actividad.creado_por or actividad.curso.profesor,
                'estado': 'completada',
            },
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

        registrar_evento_actividad(
            actividad_id=actividad_id,
            estudiante_id=estudiante.id,
            evento_tipo='completada',
            datos_adicionales={
                'puntuacion': puntuacion,
                'tiempo_empleado': tiempo_empleado,
                'es_tardia': es_tardia,
            },
        )

        # Despachar notificación a n8n de forma no-bloqueante.
        # Un fallo en n8n nunca debe interrumpir ni retrasar la respuesta al estudiante.
        try:
            enviar_resultado_actividad_n8n_async({
                'estudiante_id': estudiante.id,
                'estudiante_nombre': estudiante.nombre_completo,
                'estudiante_email': estudiante.email,
                'actividad_id': actividad.id,
                'actividad_titulo': actividad.titulo,
                'actividad_tipo': actividad.tipo,
                'curso_id': actividad.curso.id,
                'curso_nombre': actividad.curso.nombre,
                'puntuacion': puntuacion,
                'tiempo_empleado': tiempo_empleado,
                'fecha_entrega': asignacion.fecha_entrega,
                'estado': asignacion.estado,
                'es_tardia': es_tardia,
                'respuestas_detalle': respuestas_detalle,
            })
        except Exception as webhook_exc:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).error(
                'Error al despachar webhook n8n (no crítico): %s', webhook_exc
            )

        return Response(
            {
                'mensaje': 'Actividad completada exitosamente',
                'progreso': {
                    'completada': True,
                    'fecha_completado': asignacion.fecha_entrega,
                    'puntuacion': asignacion.calificacion,
                    'tiempo_empleado': tiempo_empleado,
                    'es_tardia': es_tardia,
                    'estado': asignacion.estado,
                },
            },
            status=status.HTTP_200_OK,
        )

    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes(_JWT_AUTH)
@permission_classes(_IS_AUTH)
def obtener_estadisticas_estudiante(request):
    """Obtener estadísticas de progreso del estudiante autenticado."""
    usuario = request.user

    # Admins/profesores pueden consultar estadísticas de un estudiante por query param
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
    """
    Editar o eliminar actividad.
    Profesor: Solo actividades de sus cursos.
    Administrador: Cualquier actividad.
    """
    try:
        actividad = Actividad.objects.get(id=actividad_id)

        if request.user.rol == 'profesor' and actividad.curso.profesor != request.user:
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

    if not estudiante_id or not curso_id:
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        estudiante = Usuario.objects.get(id=estudiante_id, rol='estudiante')
        curso = Curso.objects.get(id=curso_id)

        if request.user.rol == 'profesor' and curso.profesor != request.user:
            return Response(
                {'mensaje': 'Solo puedes agregar estudiantes a tus cursos'},
                status=status.HTTP_403_FORBIDDEN,
            )

        if EstudianteCurso.objects.filter(estudiante=estudiante, curso=curso).exists():
            return Response(
                {'mensaje': 'El estudiante ya está inscrito en este curso'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        inscripcion = EstudianteCurso.objects.create(estudiante=estudiante, curso=curso)
        serializer = EstudianteCursoSerializer(inscripcion)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes(_JWT_AUTH)
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def remover_estudiante_de_curso(request, inscripcion_id):
    """Remover estudiante de un curso."""
    try:
        inscripcion = EstudianteCurso.objects.get(id=inscripcion_id)

        if request.user.rol == 'profesor' and inscripcion.curso.profesor != request.user:
            return Response(
                {'mensaje': 'Solo puedes remover estudiantes de tus cursos'},
                status=status.HTTP_403_FORBIDDEN,
            )

        inscripcion.delete()
        return Response({'mensaje': 'Estudiante removido del curso exitosamente'}, status=status.HTTP_200_OK)

    except EstudianteCurso.DoesNotExist:
        return Response({'mensaje': 'Inscripción no encontrada'}, status=status.HTTP_404_NOT_FOUND)
