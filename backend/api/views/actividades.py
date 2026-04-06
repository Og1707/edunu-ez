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
from ..webhooks import enviar_resultado_actividad_a_n8n, registrar_evento_actividad


@api_view(['GET', 'POST'])
def gestionar_actividades(request):
    """Listar y crear actividades."""
    if request.method == 'GET':
        user_id = request.GET.get('user_id')

        if user_id:
            try:
                usuario = Usuario.objects.get(id=user_id)
                if usuario.rol == 'estudiante':
                    return obtener_actividades_estudiante(request)
                if usuario.rol == 'profesor':
                    return obtener_actividades_profesor(request)
                if usuario.rol == 'administrador':
                    actividades = Actividad.objects.all().order_by('-fecha_creacion')
                    serializer = ActividadSerializer(actividades, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response({'mensaje': 'Rol no reconocido'}, status=status.HTTP_403_FORBIDDEN)
            except Usuario.DoesNotExist:
                return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        actividades = Actividad.objects.all().order_by('-fecha_creacion')
        serializer = ActividadSerializer(actividades, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            usuario = Usuario.objects.get(id=user_id)
            if usuario.rol not in ['profesor', 'administrador']:
                return Response({'mensaje': 'No tienes permisos para crear actividades'}, status=status.HTTP_403_FORBIDDEN)
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

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
def obtener_actividades_profesor(request):
    """Obtener actividades de los cursos del profesor."""
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        profesor = Usuario.objects.get(id=user_id, rol='profesor')
        cursos_profesor = Curso.objects.filter(profesor=profesor)

        if not cursos_profesor.exists():
            return Response({'mensaje': 'No tienes cursos asignados'}, status=status.HTTP_404_NOT_FOUND)

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
                'porcentaje_asignado': round((asignaciones.count() / estudiantes_curso * 100) if estudiantes_curso > 0 else 0, 1)
            }
            actividades_data.append(actividad_data)

        return Response(actividades_data, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def asignar_actividad_curso(request):
    """Asignar una o varias actividades a un curso completo."""
    user_id = request.data.get('user_id')
    curso_id = request.data.get('curso_id')
    actividad_id = request.data.get('actividad_id')
    actividad_ids = request.data.get('actividad_ids', [])

    if actividad_id:
        actividad_ids = [actividad_id]
    actividad_ids = [aid for aid in actividad_ids if aid]

    if not all([user_id, curso_id]) or not actividad_ids:
        return Response({'mensaje': 'Faltan datos requeridos: user_id, curso_id y al menos una actividad'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profesor = Usuario.objects.get(id=user_id)
        if profesor.rol != 'profesor':
            return Response({'mensaje': 'Solo los profesores pueden asignar actividades'}, status=status.HTTP_403_FORBIDDEN)

        curso = Curso.objects.get(id=curso_id)
        if curso.profesor != profesor and profesor.rol != 'administrador':
            return Response({'mensaje': 'Solo puedes asignar actividades en cursos que diriges'}, status=status.HTTP_403_FORBIDDEN)

        estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).select_related('estudiante')
        if not estudiantes_curso.exists():
            return Response({'mensaje': 'No hay estudiantes inscritos en este curso'}, status=status.HTTP_400_BAD_REQUEST)

        asignaciones_creadas = []
        asignaciones_existentes = []
        errores = []
        actividades_procesadas = []

        for actividad_id in actividad_ids:
            try:
                actividad = Actividad.objects.get(id=actividad_id, curso=curso)
                actividades_procesadas.append(actividad)
            except Actividad.DoesNotExist:
                errores.append(f'Actividad {actividad_id} no encontrada o no pertenece al curso {curso.nombre}')

        if not actividades_procesadas:
            return Response({'mensaje': 'No se encontraron actividades válidas para asignar', 'errores': errores}, status=status.HTTP_400_BAD_REQUEST)

        for actividad in actividades_procesadas:
            for estudiante_curso in estudiantes_curso:
                estudiante = estudiante_curso.estudiante
                asignacion, created = AsignacionActividad.objects.get_or_create(
                    actividad=actividad,
                    estudiante=estudiante,
                    defaults={
                        'profesor': profesor,
                        'estado': 'asignada'
                    }
                )
                if created:
                    asignaciones_creadas.append({
                        'estudiante_id': estudiante.id,
                        'estudiante': estudiante.username,
                        'estudiante_nombre': estudiante.nombre_completo,
                        'email': estudiante.email
                    })
                else:
                    asignaciones_existentes.append({
                        'estudiante_id': estudiante.id,
                        'estudiante': estudiante.username,
                        'estudiante_nombre': estudiante.nombre_completo,
                        'estado_actual': asignacion.estado
                    })

        return Response({
            'mensaje': 'Actividad asignada al curso exitosamente',
            'curso': curso.nombre,
            'nuevas_asignaciones': asignaciones_creadas,
            'asignaciones_existentes': asignaciones_existentes,
            'resumen': {
                'total_estudiantes': len(estudiantes_curso),
                'nuevas_asignaciones': len(asignaciones_creadas),
                'ya_asignadas': len(asignaciones_existentes),
                'errores': len(errores)
            },
            'errores': errores
        }, status=status.HTTP_201_CREATED)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_estudiantes_curso(request):
    """Listar estudiantes de un curso específico."""
    curso_id = request.GET.get('curso_id')
    user_id = request.GET.get('user_id')

    if not all([curso_id, user_id]):
        return Response({'mensaje': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profesor = Usuario.objects.get(id=user_id)
        if profesor.rol != 'profesor':
            return Response({'mensaje': 'Solo los profesores pueden ver estudiantes'}, status=status.HTTP_403_FORBIDDEN)

        curso = Curso.objects.get(id=curso_id)
        estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).select_related('estudiante')

        estudiantes_data = []
        for ec in estudiantes_curso:
            estudiante = ec.estudiante
            estudiantes_data.append({
                'id': estudiante.id,
                'username': estudiante.username,
                'nombre_completo': estudiante.nombre_completo,
                'email': estudiante.email,
                'fecha_inscripcion': ec.fecha_inscripcion
            })

        return Response({'curso': curso.nombre, 'estudiantes': estudiantes_data, 'total_estudiantes': len(estudiantes_data)}, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def actividades_asignadas_estudiante(request):
    """Obtener actividades asignadas a un estudiante."""
    user_id = request.GET.get('user_id')

    if not user_id:
        return Response({'mensaje': 'ID de usuario requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related('actividad', 'actividad__curso', 'profesor').order_by('-fecha_asignacion')

        actividades_data = []
        for asignacion in asignaciones:
            actividad = asignacion.actividad
            actividades_data.append({
                'asignacion_id': asignacion.id,
                'actividad_id': actividad.id,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'tipo': actividad.tipo,
                'tipo_display': dict(actividad.TIPOS).get(actividad.tipo),
                'curso': actividad.curso.nombre,
                'profesor': asignacion.profesor.nombre_completo,
                'fecha_asignacion': asignacion.fecha_asignacion,
                'fecha_limite': actividad.fecha_limite,
                'estado': asignacion.estado,
                'estado_display': dict(asignacion.ESTADOS_ASIGNACION).get(asignacion.estado),
                'calificacion': asignacion.calificacion,
                'comentarios_profesor': asignacion.comentarios_profesor,
                'tiene_entrega': bool(asignacion.archivo_entrega)
            })

        return Response({'actividades_asignadas': actividades_data, 'total_actividades': len(actividades_data)}, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def actividades_curso_profesor(request):
    """Obtener actividades de un curso para el profesor."""
    user_id = request.GET.get('user_id')
    curso_id = request.GET.get('curso_id')

    if not user_id:
        return Response({'mensaje': 'ID de usuario requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        profesor = Usuario.objects.get(id=user_id)
        if profesor.rol != 'profesor':
            return Response({'mensaje': 'Solo los profesores pueden ver actividades de cursos'}, status=status.HTTP_403_FORBIDDEN)

        cursos = Curso.objects.filter(id=curso_id, profesor=profesor) if curso_id else Curso.objects.filter(profesor=profesor)

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
                        'porcentaje_asignado': round((total_asignaciones / total_estudiantes_curso * 100) if total_estudiantes_curso > 0 else 0, 1),
                        'esta_asignada_completa': total_asignaciones == total_estudiantes_curso
                    }
                })

            cursos_data.append({
                'curso_id': curso.id,
                'curso_nombre': curso.nombre,
                'total_estudiantes': EstudianteCurso.objects.filter(curso=curso).count(),
                'actividades': actividades_data,
                'total_actividades': len(actividades_data)
            })

        return Response({'profesor': profesor.nombre_completo, 'cursos': cursos_data, 'total_cursos': len(cursos_data)}, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def obtener_actividades_estudiante(request):
    """Obtener todas las actividades asignadas a un estudiante."""
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    request_user_id = request.user.id if request.user.is_authenticated else None
    if request_user_id and request_user_id != int(user_id):
        try:
            request_user = Usuario.objects.get(id=request_user_id)
            if request_user.rol not in ['profesor', 'administrador']:
                return Response({'mensaje': 'No tienes permisos para ver estas actividades'}, status=status.HTTP_403_FORBIDDEN)
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related('actividad', 'actividad__curso')

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
                'fecha_asignacion': asignacion.fecha_asignacion
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

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def iniciar_actividad_estudiante(request):
    """Marcar que un estudiante ha iniciado una actividad."""
    user_id = request.data.get('user_id')
    actividad_id = request.data.get('actividad_id')

    if not user_id or not actividad_id:
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        actividad = Actividad.objects.get(id=actividad_id)

        if not EstudianteCurso.objects.filter(estudiante=estudiante, curso=actividad.curso).exists():
            return Response({'mensaje': 'No tienes acceso a esta actividad'}, status=status.HTTP_403_FORBIDDEN)

        asignacion, created = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': actividad.creado_por or actividad.curso.profesor,
                'estado': 'en_progreso'
            }
        )

        if not created and asignacion.estado == 'asignada':
            asignacion.estado = 'en_progreso'
            asignacion.save()

        return Response({
            'mensaje': 'Actividad iniciada exitosamente',
            'progreso': {
                'estado': asignacion.estado,
                'fecha_asignacion': asignacion.fecha_asignacion
            }
        }, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def completar_actividad_estudiante(request):
    """Marcar una actividad como completada por el estudiante."""
    user_id = request.data.get('user_id')
    actividad_id = request.data.get('actividad_id')
    puntuacion = request.data.get('puntuacion', 0)
    tiempo_empleado = request.data.get('tiempo_empleado', 0)
    respuestas_detalle = request.data.get('respuestas_detalle', [])

    if not user_id or not actividad_id:
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        actividad = Actividad.objects.get(id=actividad_id)

        if not EstudianteCurso.objects.filter(estudiante=estudiante, curso=actividad.curso).exists():
            return Response({'mensaje': 'No tienes acceso a esta actividad'}, status=status.HTTP_403_FORBIDDEN)

        if actividad.fecha_limite and actividad.fecha_limite < timezone.now().date():
            es_tardia = True
        else:
            es_tardia = False

        asignacion, created = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': actividad.creado_por or actividad.curso.profesor,
                'estado': 'completada'
            }
        )

        asignacion.estado = 'completada'
        asignacion.fecha_entrega = timezone.now()
        asignacion.calificacion = puntuacion
        if es_tardia:
            asignacion.comentarios_estudiante = f'Entregada tarde. Tiempo empleado: {tiempo_empleado} minutos'
        else:
            asignacion.comentarios_estudiante = f'Tiempo empleado: {tiempo_empleado} minutos'
        asignacion.save()

        registrar_evento_actividad(
            actividad_id=actividad_id,
            estudiante_id=user_id,
            evento_tipo='completada',
            datos_adicionales={
                'puntuacion': puntuacion,
                'tiempo_empleado': tiempo_empleado,
                'es_tardia': es_tardia
            }
        )

        actividad_data = {
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
            'respuestas_detalle': respuestas_detalle
        }

        webhook_result = enviar_resultado_actividad_a_n8n(actividad_data)
        webhook_info = {
            'enviado': webhook_result['success'],
            'mensaje': webhook_result['message'],
            'codigo': webhook_result.get('response_code', 0)
        }

        return Response({
            'mensaje': 'Actividad completada exitosamente',
            'progreso': {
                'completada': True,
                'fecha_completado': asignacion.fecha_entrega,
                'puntuacion': asignacion.calificacion,
                'tiempo_empleado': tiempo_empleado,
                'es_tardia': es_tardia,
                'estado': asignacion.estado
            },
            'webhook': webhook_info
        }, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def obtener_estadisticas_estudiante(request):
    """Obtener estadísticas de progreso del estudiante."""
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    request_user_id = request.user.id if request.user.is_authenticated else None
    if request_user_id and request_user_id != int(user_id):
        try:
            request_user = Usuario.objects.get(id=request_user_id)
            if request_user.rol not in ['profesor', 'administrador']:
                return Response({'mensaje': 'Solo puedes ver tus propias estadísticas'}, status=status.HTTP_403_FORBIDDEN)
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related('actividad')

        total_actividades = asignaciones.count()
        actividades_completadas = asignaciones.filter(estado__in=['completada', 'revisada', 'calificada']).count()
        actividades_pendientes = total_actividades - actividades_completadas

        fecha_limite = timezone.now().date() + timezone.timedelta(days=7)
        actividades_por_vencer = asignaciones.filter(
            actividad__fecha_limite__lte=fecha_limite,
            actividad__fecha_limite__gte=timezone.now().date(),
            estado__in=['asignada', 'en_progreso']
        ).count()

        actividades_vencidas = asignaciones.filter(
            actividad__fecha_limite__lt=timezone.now().date(),
            estado__in=['asignada', 'en_progreso']
        ).count()

        puntuacion_promedio = asignaciones.filter(
            estado__in=['completada', 'revisada', 'calificada'],
            calificacion__isnull=False
        ).aggregate(promedio=Avg('calificacion'))['promedio'] or 0

        return Response({
            'actividades_completadas': actividades_completadas,
            'actividades_pendientes': actividades_pendientes,
            'actividades_por_vencer': actividades_por_vencer,
            'actividades_vencidas': actividades_vencidas,
            'puntuacion_promedio': round(puntuacion_promedio, 2),
            'porcentaje_completado': round((actividades_completadas / total_actividades * 100) if total_actividades > 0 else 0, 2)
        }, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT', 'DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def gestionar_actividad_especifica(request, actividad_id):
    """
    Editar o eliminar actividad
    Profesor: Solo actividades de sus cursos
    Administrador: Cualquier actividad
    """
    try:
        actividad = Actividad.objects.get(id=actividad_id)

        if request.usuario.rol == 'profesor' and actividad.curso.profesor != request.usuario:
            return Response({'mensaje': 'Solo puedes gestionar actividades de tus cursos'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'PUT':
            serializer = ActividadSerializer(actividad, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            actividad.delete()
            return Response({'mensaje': 'Actividad eliminada exitosamente'}, status=status.HTTP_200_OK)

    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def agregar_estudiante_a_curso(request):
    """
    Agregar estudiante a un curso
    """
    estudiante_id = request.data.get('estudiante_id')
    curso_id = request.data.get('curso_id')

    if not estudiante_id or not curso_id:
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        estudiante = Usuario.objects.get(id=estudiante_id, rol='estudiante')
        curso = Curso.objects.get(id=curso_id)

        if request.usuario.rol == 'profesor' and curso.profesor != request.usuario:
            return Response({'mensaje': 'Solo puedes agregar estudiantes a tus cursos'}, status=status.HTTP_403_FORBIDDEN)

        if EstudianteCurso.objects.filter(estudiante=estudiante, curso=curso).exists():
            return Response({'mensaje': 'El estudiante ya está inscrito en este curso'}, status=status.HTTP_400_BAD_REQUEST)

        inscripcion = EstudianteCurso.objects.create(estudiante=estudiante, curso=curso)
        serializer = EstudianteCursoSerializer(inscripcion)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def remover_estudiante_de_curso(request, inscripcion_id):
    """
    Remover estudiante de un curso
    """
    try:
        inscripcion = EstudianteCurso.objects.get(id=inscripcion_id)

        if request.usuario.rol == 'profesor' and inscripcion.curso.profesor != request.usuario:
            return Response({'mensaje': 'Solo puedes remover estudiantes de tus cursos'}, status=status.HTTP_403_FORBIDDEN)

        inscripcion.delete()
        return Response({'mensaje': 'Estudiante removido del curso exitosamente'}, status=status.HTTP_200_OK)

    except EstudianteCurso.DoesNotExist:
        return Response({'mensaje': 'Inscripción no encontrada'}, status=status.HTTP_404_NOT_FOUND)
