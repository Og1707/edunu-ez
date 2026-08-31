from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from api.permissions import IsAdministrador, IsProfesor
from api.models import Curso, MateriaCienciasNaturales
from api.serializers import CursoSerializer
from api.services.cursos_service import CursosService
from api.services.cache_service import CacheService


@api_view(['GET'])
def listar_cursos(request):
    """Endpoint para listar todos los cursos disponibles optimizado con caching y select_related."""
    cursos_data = CursosService.listar_cursos_optimizados()
    return Response(cursos_data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def crear_curso(request):
    """Endpoint para crear un nuevo curso de manera atómica con invalidación de caché."""
    curso = CursosService.crear_curso(creador=request.user, datos=request.data)
    serializer = CursoSerializer(curso)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def gestionar_curso_especifico(request, curso_id):
    """
    Editar o eliminar curso.
    Profesor: Solo sus propios cursos.
    Administrador: Cualquier curso.
    """
    try:
        curso = Curso.objects.select_related('profesor').get(id=curso_id)

        if request.user.rol == 'profesor' and curso.profesor != request.user:
            return Response({'mensaje': 'Solo puedes gestionar tus propios cursos'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'PUT':
            serializer = CursoSerializer(curso, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                CacheService.invalidar_cursos()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            curso.delete()
            CacheService.invalidar_cursos()
            return Response({'mensaje': 'Curso eliminado exitosamente'}, status=status.HTTP_200_OK)

    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsAdministrador])
def asignar_profesor_a_curso(request, curso_id):
    """Asignar profesor a un curso (solo administrador)."""
    profesor_id = request.data.get('profesor_id')

    if not profesor_id:
        return Response({'mensaje': 'ID del profesor requerido'}, status=status.HTTP_400_BAD_REQUEST)

    curso = CursosService.asignar_profesor(curso_id=curso_id, profesor_id=profesor_id)
    serializer = CursoSerializer(curso)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def gestionar_materias_ciencias(request):
    """Listar y crear materias de ciencias naturales optimizado sin N+1."""
    if request.method == 'GET':
        area = request.GET.get('area', '')
        nivel = request.GET.get('nivel', '')
        materias_data = CursosService.listar_materias_ciencias(area=area, nivel=nivel)
        return Response(materias_data, status=status.HTTP_200_OK)

    # POST — requiere autenticación y rol administrador
    if not (hasattr(request, 'user') and request.user and request.user.is_authenticated):
        return Response({'mensaje': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    if request.user.rol != 'administrador':
        return Response(
            {'mensaje': 'Solo los administradores pueden crear materias'},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        materia = MateriaCienciasNaturales.objects.create(
            nombre=request.data.get('nombre'),
            area=request.data.get('area'),
            nivel_educativo=request.data.get('nivel_educativo'),
            descripcion=request.data.get('descripcion', ''),
            temas_principales=request.data.get('temas_principales', []),
            objetivos_aprendizaje=request.data.get('objetivos_aprendizaje', ''),
            recursos_recomendados=request.data.get('recursos_recomendados', [])
        )
        CacheService.invalidar_materias_ciencias()

        return Response({
            'mensaje': 'Materia creada exitosamente',
            'materia_id': materia.id,
            'nombre': materia.nombre,
            'area': materia.get_area_display(),
            'nivel': materia.get_nivel_educativo_display()
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'mensaje': f'Error al crear la materia: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def obtener_areas_ciencias(request):
    """Obtener las áreas de ciencias naturales disponibles con caché Redis."""
    areas = CursosService.obtener_areas_ciencias()
    return Response(areas, status=status.HTTP_200_OK)


@api_view(['GET'])
def obtener_niveles_educativos(request):
    """Obtener los niveles educativos disponibles con caché Redis."""
    niveles = CursosService.obtener_niveles_educativos()
    return Response(niveles, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def crear_curso_ciencias(request):
    """Crear un curso de ciencias naturales de forma atómica."""
    resultado = CursosService.crear_curso_ciencias(usuario=request.user, datos=request.data)
    return Response(resultado, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def obtener_temas_sugeridos(request):
    """Obtener temas sugeridos basados en el área de ciencias con caché Redis."""
    area = request.GET.get('area', '')
    temas = CursosService.obtener_temas_sugeridos(area=area)
    return Response({'area': area, 'temas_sugeridos': temas}, status=status.HTTP_200_OK)
