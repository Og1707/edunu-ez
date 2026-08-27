"""
Vistas para el sistema de plantillas de actividades.
Maneja la creación y gestión de actividades multimedia y de texto.
"""
from django.db import transaction
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from api.permissions import IsAdministrador, IsProfesor
from ..models import (
    Actividad, ActividadMultimedia, ActividadTexto,
    Pregunta, OpcionRespuesta, Usuario, Curso
)
from ..serializers import (
    ActividadMultimediaCreateSerializer, ActividadTextoCreateSerializer,
    ActividadCompletaSerializer, PreguntaSerializer, OpcionRespuestaSerializer,
    PreguntaCreateSerializer
)
from ..utils.cloudinary_utils import upload_multimedia_file, delete_cloudinary_file
from ..utils.validators import validate_multimedia_file


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def crear_actividad_multimedia(request):
    """
    Crear una actividad multimedia con archivo y preguntas.
    Requiere archivo multimedia y al menos una pregunta con opciones.
    """
    usuario = request.user
    if not usuario or usuario.rol not in ['profesor', 'administrador']:
        return Response({'mensaje': 'No tienes permisos para crear actividades'}, status=status.HTTP_403_FORBIDDEN)

    # Verificar que se incluya un archivo multimedia
    if 'archivo_multimedia' not in request.FILES:
        return Response({'mensaje': 'Se requiere un archivo multimedia'}, status=status.HTTP_400_BAD_REQUEST)

    archivo = request.FILES['archivo_multimedia']

    try:
        with transaction.atomic():
            # 1. Preparar datos para el serializer (antes de subir a Cloudinary)
            data = {}
            
            # Convertir QueryDict a diccionario normal
            for key, value in request.data.items():
                if key == 'archivo_multimedia':
                    continue  # Saltar archivos, se manejan por separado
                elif key == 'preguntas':
                    if isinstance(value, str):
                        import json
                        try:
                            data[key] = json.loads(value)
                        except json.JSONDecodeError:
                            data[key] = value
                    elif isinstance(value, list) and len(value) == 1 and isinstance(value[0], list):
                        # Si está anidado como [[...]], tomar el primer elemento
                        data[key] = value[0]
                    else:
                        data[key] = value
                elif isinstance(value, list) and len(value) == 1:
                    # Si es una lista con un solo elemento, tomar el valor directo
                    data[key] = value[0]
                else:
                    data[key] = value

            # 2. Validar datos con el serializer ANTES de subir a Cloudinary
            serializer = ActividadMultimediaCreateSerializer(data=data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # 3. Subir archivo a Cloudinary solo si la validación es exitosa
            cloudinary_response = upload_multimedia_file(
                archivo,
                public_id_prefix='actividades',
                tags=['actividad', 'multimedia', f'usuario_{usuario.id}']
            )

            # 4. Crear actividad con el usuario como parámetro (no en data)
            actividad = serializer.save(creado_por=usuario)

            # 5. Crear registro de ActividadMultimedia
            ActividadMultimedia.objects.create(
                actividad=actividad,
                archivo_url_cloudinary=cloudinary_response['secure_url'],
                tipo_archivo=cloudinary_response['file_type'],
                duracion_segundos=cloudinary_response.get('duration'),
                tamaño_bytes=cloudinary_response.get('bytes')
            )

            # 6. Retornar actividad completa
            actividad_completa = ActividadCompletaSerializer(actividad)
            return Response({
                'mensaje': 'Actividad multimedia creada exitosamente',
                'actividad': actividad_completa.data,
                'cloudinary_info': cloudinary_response
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        # Si hay error, intentar eliminar el archivo de Cloudinary si se subió
        if 'cloudinary_response' in locals():
            try:
                delete_cloudinary_file(cloudinary_response['public_id'])
            except:
                pass  # Ignorar errores al limpiar

        return Response({
            'mensaje': f'Error al crear actividad multimedia: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def crear_actividad_texto(request):
    """
    Crear una actividad de texto con preguntas.
    No requiere archivo multimedia, solo preguntas con opciones.
    """
    usuario = request.user
    if not usuario or usuario.rol not in ['profesor', 'administrador']:
        return Response({'mensaje': 'No tienes permisos para crear actividades'}, status=status.HTTP_403_FORBIDDEN)

    try:
        with transaction.atomic():
            # Preparar datos para el serializer
            data = request.data.copy()
            data['creado_por'] = usuario.id

            # Crear actividad con preguntas usando el serializer
            serializer = ActividadTextoCreateSerializer(data=data)
            if serializer.is_valid():
                actividad = serializer.save(creado_por=usuario)

                # Crear registro de ActividadTexto (opcional, solo si hay tiempo límite)
                tiempo_limite = data.get('tiempo_limite_minutos')
                if tiempo_limite:
                    ActividadTexto.objects.create(
                        actividad=actividad,
                        tiempo_limite_minutos=tiempo_limite
                    )

                # Retornar actividad completa
                actividad_completa = ActividadCompletaSerializer(actividad)
                return Response({
                    'mensaje': 'Actividad de texto creada exitosamente',
                    'actividad': actividad_completa.data
                }, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'mensaje': f'Error al crear actividad de texto: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def obtener_actividad_completa(request, actividad_id):
    """
    Obtener una actividad completa con toda su información según la plantilla.
    """
    try:
        actividad = Actividad.objects.get(id=actividad_id)
        serializer = ActividadCompletaSerializer(actividad)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def obtener_actividades_por_plantilla(request):
    """
    Obtener actividades filtradas por tipo de plantilla.
    Parámetros de query:
    - template_type: 'legacy', 'multimedia', 'texto'
    - curso_id: ID del curso (opcional)
    """
    template_type = request.GET.get('template_type')
    curso_id = request.GET.get('curso_id')
    usuario = request.user

    if not usuario:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    # Filtrar actividades según permisos del usuario
    actividades = Actividad.objects.all()

    if usuario.rol == 'profesor':
        actividades = actividades.filter(creado_por=usuario)
    elif usuario.rol == 'estudiante':
        # Para estudiantes, solo actividades asignadas
        from ..models import AsignacionActividad
        actividades_asignadas = AsignacionActividad.objects.filter(
            estudiante=usuario
        ).values_list('actividad_id', flat=True)
        actividades = actividades.filter(id__in=actividades_asignadas)

    # Aplicar filtros
    if template_type:
        actividades = actividades.filter(template_type=template_type)

    if curso_id:
        actividades = actividades.filter(curso_id=curso_id)

    actividades = actividades.order_by('-fecha_creacion')
    serializer = ActividadCompletaSerializer(actividades, many=True)

    return Response({
        'actividades': serializer.data,
        'total': len(serializer.data),
        'filtros': {
            'template_type': template_type,
            'curso_id': curso_id
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def agregar_pregunta_a_actividad(request, actividad_id):
    """
    Agregar una nueva pregunta a una actividad existente.
    """
    usuario = request.user
    if not usuario or usuario.rol not in ['profesor', 'administrador']:
        return Response({'mensaje': 'No tienes permisos para modificar actividades'}, status=status.HTTP_403_FORBIDDEN)

    try:
        actividad = Actividad.objects.get(id=actividad_id)

        # Verificar permisos
        if actividad.creado_por != usuario:
            return Response({'mensaje': 'No tienes permisos para modificar esta actividad'}, status=status.HTTP_403_FORBIDDEN)

        # Crear pregunta con opciones
        data = request.data.copy()
        data['actividad'] = actividad_id

        serializer = PreguntaCreateSerializer(data=data)
        if serializer.is_valid():
            pregunta = serializer.save()
            return Response({
                'mensaje': 'Pregunta agregada exitosamente',
                'pregunta': PreguntaSerializer(pregunta).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def eliminar_pregunta(request, pregunta_id):
    """
    Eliminar una pregunta de una actividad.
    """
    usuario = request.user
    if not usuario or usuario.rol not in ['profesor', 'administrador']:
        return Response({'mensaje': 'No tienes permisos para modificar actividades'}, status=status.HTTP_403_FORBIDDEN)

    try:
        pregunta = Pregunta.objects.get(id=pregunta_id)
        actividad = pregunta.actividad

        # Verificar permisos
        if actividad.creado_por != usuario:
            return Response({'mensaje': 'No tienes permisos para modificar esta actividad'}, status=status.HTTP_403_FORBIDDEN)

        pregunta.delete()

        return Response({
            'mensaje': 'Pregunta eliminada exitosamente'
        }, status=status.HTTP_200_OK)

    except Pregunta.DoesNotExist:
        return Response({'mensaje': 'Pregunta no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def obtener_firma_cloudinary(request):
    """
    Obtener firma para uploads no firmados desde el cliente.
    Útil para uploads directos desde el frontend.
    """
    from ..utils.cloudinary_utils import get_upload_signature

    try:
        firma = get_upload_signature()
        return Response(firma, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            'mensaje': f'Error al generar firma: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)