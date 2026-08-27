"""
Endpoints REST adicionales para el sistema de plantillas de actividades.
Completa el Paso 4 del sistema de plantillas.
"""
from django.db import transaction
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

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


class ActividadPagination(PageNumberPagination):
    """Paginación personalizada para actividades."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def listar_plantillas_disponibles(request):
    """
    Listar todas las plantillas de actividades disponibles.
    Retorna información sobre los tipos de plantillas y sus capacidades.
    """
    plantillas = {
        'multimedia': {
            'nombre': 'Actividad Multimedia',
            'descripcion': 'Actividades con video/imagen y preguntas interactivas',
            'requiere_archivo': True,
            'tipos_archivo': ['image', 'video', 'audio'],
            'max_tamaño_mb': 100,
            'preguntas_requeridas': True,
            'min_preguntas': 1,
            'max_preguntas': 20
        },
        'texto': {
            'nombre': 'Actividad de Texto',
            'descripcion': 'Actividades basadas en texto con tiempo límite',
            'requiere_archivo': False,
            'tiempo_limite_opcional': True,
            'min_tiempo': 5,
            'max_tiempo': 180,
            'preguntas_requeridas': True,
            'min_preguntas': 1,
            'max_preguntas': 50
        },
        'legacy': {
            'nombre': 'Actividad Heredada',
            'descripcion': 'Formato tradicional de actividades',
            'requiere_archivo': False,
            'preguntas_requeridas': False
        }
    }
    
    return Response({
        'plantillas': plantillas,
        'total': len(plantillas)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def preview_plantilla_multimedia(request):
    """
    Previsualizar una actividad multimedia antes de guardar.
    Valida solo la estructura de preguntas/opciones sin requerir campos de BD.
    """
    titulo = request.GET.get('titulo', '')
    descripcion = request.GET.get('descripcion', '')
    preguntas_json = request.GET.get('preguntas', '[]')

    import json
    try:
        preguntas_data = json.loads(preguntas_json)
    except json.JSONDecodeError:
        return Response({
            'valido': False,
            'mensaje': 'JSON de preguntas inválido'
        }, status=status.HTTP_400_BAD_REQUEST)

    errores = []

    # Validar que cada pregunta tenga al menos 2 opciones y 1 correcta
    for i, pregunta in enumerate(preguntas_data):
        opciones = pregunta.get('opciones', [])
        if len(opciones) < 2:
            errores.append(
                f"Pregunta {i + 1}: debe tener al menos 2 opciones (tiene {len(opciones)})"
            )
            continue
        correctas = [o for o in opciones if o.get('es_correcta')]
        if len(correctas) != 1:
            errores.append(
                f"Pregunta {i + 1}: debe tener exactamente 1 opción correcta (tiene {len(correctas)})"
            )

    if errores:
        return Response({
            'valido': False,
            'errores': errores,
            'mensaje': 'Estructura inválida'
        }, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        'valido': True,
        'mensaje': 'Estructura válida',
        'preview': {
            'titulo': titulo,
            'descripcion': descripcion,
            'tipo': 'video',
            'template_type': 'multimedia',
            'preguntas': preguntas_data,
        },
        'preguntas_count': len(preguntas_data),
        'opciones_total': sum(len(p.get('opciones', [])) for p in preguntas_data),
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def duplicar_actividad(request, actividad_id):
    """
    Duplicar una actividad existente con sus preguntas.
    Permite crear una nueva actividad basada en una existente.
    """
    usuario = request.user
    if not usuario or usuario.rol not in ['profesor', 'administrador']:
        return Response({'mensaje': 'No tienes permisos para duplicar actividades'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        actividad_original = Actividad.objects.get(id=actividad_id)
        
        # Verificar permisos
        if actividad_original.creado_por != usuario and usuario.rol != 'administrador':
            return Response({'mensaje': 'No puedes duplicar esta actividad'}, status=status.HTTP_403_FORBIDDEN)
        
        with transaction.atomic():
            # Obtener preguntas originales
            preguntas_originales = []
            for pregunta in actividad_original.preguntas.all():
                opciones_data = []
                for opcion in pregunta.opciones.all():
                    opciones_data.append({
                        'texto': opcion.texto,
                        'es_correcta': opcion.es_correcta,
                        'orden': opcion.orden
                    })
                
                preguntas_originales.append({
                    'enunciado': pregunta.enunciado,
                    'orden': pregunta.orden,
                    'opciones': opciones_data
                })
            
            # Determinar tipo de serializer según template_type
            if actividad_original.template_type == 'multimedia':
                # Verificar si tiene multimedia
                try:
                    multimedia = ActividadMultimedia.objects.get(actividad=actividad_original)
                    # Para multimedia, necesitamos nuevo archivo
                    return Response({
                        'mensaje': 'requiere un nuevo archivo para duplicar',
                        'actividad_original': {
                            'id': actividad_original.id,
                            'titulo': actividad_original.titulo,
                            'descripcion': actividad_original.descripcion,
                            'template_type': actividad_original.template_type,
                            'preguntas': preguntas_originales
                        }
                    }, status=status.HTTP_200_OK)
                except ActividadMultimedia.DoesNotExist:
                    pass
            
            # Para actividades de texto o legacy
            data = {
                'titulo': f"{actividad_original.titulo} (Copia)",
                'descripcion': actividad_original.descripcion,
                'tipo': actividad_original.tipo,
                'template_type': actividad_original.template_type,
                'curso': actividad_original.curso.id,
                'preguntas': preguntas_originales
            }
            
            if actividad_original.template_type == 'texto':
                serializer = ActividadTextoCreateSerializer(data=data)
            else:
                # Legacy - usar serializer básico
                from ..serializers import ActividadSerializer
                data.pop('preguntas')  # Legacy no usa preguntas en serializer principal
                serializer = ActividadSerializer(data=data)
            
            if serializer.is_valid():
                nueva_actividad = serializer.save(creado_por=usuario)

                # Las preguntas ya fueron creadas por el mixin del serializer.
                # Solo recrearlas para actividades legacy (que usan ActividadSerializer
                # básico sin mixin).
                if actividad_original.template_type not in ('texto', 'multimedia'):
                    for pregunta_data in preguntas_originales:
                        pregunta_serializer = PreguntaCreateSerializer(data=pregunta_data)
                        if pregunta_serializer.is_valid():
                            pregunta_serializer.save(actividad=nueva_actividad)
                        else:
                            raise Exception(f"Error al crear pregunta: {pregunta_serializer.errors}")
                
                return Response({
                    'mensaje': 'Actividad duplicada exitosamente',
                    'actividad_original': ActividadCompletaSerializer(actividad_original).data,
                    'nueva_actividad': ActividadCompletaSerializer(nueva_actividad).data
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def estadisticas_plantillas(request):
    """
    Obtener estadísticas del uso de plantillas.
    Útil para dashboard administrativo.
    """
    usuario = request.user
    if not usuario or usuario.rol not in ['administrador']:
        return Response({'mensaje': 'No tienes permisos para ver estadísticas'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Estadísticas por template_type
        stats_por_tipo = {}
        for template_choice, _ in Actividad.TEMPLATE_TYPES:
            count = Actividad.objects.filter(template_type=template_choice).count()
            stats_por_tipo[template_choice] = count
        
        # Estadísticas generales
        total_actividades = Actividad.objects.count()
        total_preguntas = Pregunta.objects.count()
        total_opciones = OpcionRespuesta.objects.count()
        
        # Estadísticas por mes (últimos 6 meses)
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        from django.utils import timezone
        from datetime import timedelta
        
        seis_meses_atras = timezone.now() - timedelta(days=180)
        actividades_por_mes = Actividad.objects.filter(
            fecha_creacion__gte=seis_meses_atras
        ).annotate(
            month=TruncMonth('fecha_creacion')
        ).values('month').annotate(count=Count('id')).order_by('month')
        
        return Response({
            'generales': {
                'total_actividades': total_actividades,
                'total_preguntas': total_preguntas,
                'total_opciones': total_opciones,
                'promedio_preguntas_por_actividad': round(total_preguntas / max(total_actividades, 1), 2),
                'promedio_opciones_por_pregunta': round(total_opciones / max(total_preguntas, 1), 2)
            },
            'por_tipo_plantilla': stats_por_tipo,
            'actividades_ultimos_6_meses': list(actividades_por_mes)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'mensaje': f'Error al obtener estadísticas: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def buscar_actividades_plantillas(request):
    """
    Buscar actividades por texto con filtros de plantilla.
    Soporta búsqueda全文 y filtrado avanzado.
    """
    usuario = request.user
    if not usuario:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Parámetros de búsqueda
    query = request.GET.get('q', '').strip()
    template_type = request.GET.get('template_type')
    curso_id = request.GET.get('curso_id')
    page = request.GET.get('page', 1)
    
    # Base queryset con permisos
    actividades = Actividad.objects.all()

    if usuario.rol == 'profesor':
        actividades = actividades.filter(creado_por=usuario)
    elif usuario.rol == 'estudiante':
        from ..models import AsignacionActividad
        from django.db.models import Q as ModelQ
        actividades_asignadas = AsignacionActividad.objects.filter(
            estudiante=usuario
        ).values_list('actividad_id', flat=True)
        actividades = actividades.filter(id__in=list(actividades_asignadas))

    # Aplicar filtros de texto con Q para evitar expandir el queryset con |
    from django.db.models import Q as ModelQ
    if query:
        actividades = actividades.filter(
            ModelQ(titulo__icontains=query) | ModelQ(descripcion__icontains=query)
        )

    if template_type:
        actividades = actividades.filter(template_type=template_type)

    if curso_id:
        actividades = actividades.filter(curso_id=curso_id)
    
    # Paginación
    paginator = ActividadPagination()
    result_page = paginator.paginate_queryset(actividades.order_by('-fecha_creacion'), request)

    serializer = ActividadCompletaSerializer(result_page, many=True)

    paginated = paginator.get_paginated_response(serializer.data)
    paginated.data['query'] = query
    paginated.data['filtros'] = {
        'template_type': template_type,
        'curso_id': curso_id,
    }
    return paginated
