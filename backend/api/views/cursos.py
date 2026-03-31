from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .auth import verificar_permisos
from ..models import Curso, Usuario, MateriaCienciasNaturales, CursoCienciasNaturales
from ..serializers import CursoSerializer


@api_view(['GET'])
def listar_cursos(request):
    """Endpoint para listar todos los cursos disponibles."""
    cursos = Curso.objects.all().order_by('nombre')
    serializer = CursoSerializer(cursos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def crear_curso(request):
    """Endpoint para crear un nuevo curso."""
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        usuario = Usuario.objects.get(id=user_id)
        if usuario.rol not in ['profesor', 'administrador']:
            return Response({'mensaje': 'No tienes permisos para crear cursos'}, status=status.HTTP_403_FORBIDDEN)
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    datos_curso = request.data.copy()
    if usuario.rol == 'administrador' and datos_curso.get('profesor'):
        try:
            profesor = Usuario.objects.get(id=datos_curso['profesor'], rol='profesor')
            datos_curso['profesor'] = profesor.id
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    elif usuario.rol == 'profesor':
        datos_curso['profesor'] = usuario.id

    serializer = CursoSerializer(data=datos_curso)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@verificar_permisos(['profesor', 'administrador'])
def gestionar_curso_especifico(request, curso_id):
    """
    Editar o eliminar curso.
    Profesor: Solo sus propios cursos.
    Administrador: Cualquier curso.
    """
    try:
        curso = Curso.objects.get(id=curso_id)

        if request.usuario.rol == 'profesor' and curso.profesor != request.usuario:
            return Response({'mensaje': 'Solo puedes gestionar tus propios cursos'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'PUT':
            serializer = CursoSerializer(curso, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            curso.delete()
            return Response({'mensaje': 'Curso eliminado exitosamente'}, status=status.HTTP_200_OK)

    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@verificar_permisos(['administrador'])
def asignar_profesor_a_curso(request, curso_id):
    """Asignar profesor a un curso (solo administrador)."""
    profesor_id = request.data.get('profesor_id')

    if not profesor_id:
        return Response({'mensaje': 'ID del profesor requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        curso = Curso.objects.get(id=curso_id)
        profesor = Usuario.objects.get(id=profesor_id, rol='profesor')

        curso.profesor = profesor
        curso.save()

        serializer = CursoSerializer(curso)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def gestionar_materias_ciencias(request):
    """Listar y crear materias de ciencias naturales."""
    if request.method == 'GET':
        area = request.GET.get('area', '')
        nivel = request.GET.get('nivel', '')

        materias = MateriaCienciasNaturales.objects.filter(activa=True)
        if area:
            materias = materias.filter(area=area)
        if nivel:
            materias = materias.filter(nivel_educativo=nivel)

        materias = materias.order_by('area', 'nivel_educativo', 'nombre')
        materias_data = []
        for materia in materias:
            materias_data.append({
                'id': materia.id,
                'nombre': materia.nombre,
                'area': materia.area,
                'area_display': materia.get_area_display(),
                'nivel_educativo': materia.nivel_educativo,
                'nivel_display': materia.get_nivel_educativo_display(),
                'descripcion': materia.descripcion,
                'temas_principales': materia.temas_principales,
                'objetivos_aprendizaje': materia.objetivos_aprendizaje,
                'recursos_recomendados': materia.recursos_recomendados,
                'fecha_creacion': materia.fecha_creacion,
                'total_cursos': materia.cursos.count()
            })
        return Response(materias_data, status=status.HTTP_200_OK)

    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        usuario = Usuario.objects.get(id=user_id)
        if usuario.rol != 'administrador':
            return Response({'mensaje': 'Solo los administradores pueden crear materias'}, status=status.HTTP_403_FORBIDDEN)

        materia = MateriaCienciasNaturales.objects.create(
            nombre=request.data.get('nombre'),
            area=request.data.get('area'),
            nivel_educativo=request.data.get('nivel_educativo'),
            descripcion=request.data.get('descripcion', ''),
            temas_principales=request.data.get('temas_principales', []),
            objetivos_aprendizaje=request.data.get('objetivos_aprendizaje', ''),
            recursos_recomendados=request.data.get('recursos_recomendados', [])
        )

        return Response({
            'mensaje': 'Materia creada exitosamente',
            'materia_id': materia.id,
            'nombre': materia.nombre,
            'area': materia.get_area_display(),
            'nivel': materia.get_nivel_educativo_display()
        }, status=status.HTTP_201_CREATED)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error al crear la materia: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def obtener_areas_ciencias(request):
    """Obtener las áreas de ciencias naturales disponibles."""
    areas = [{'value': area[0], 'label': area[1]} for area in MateriaCienciasNaturales.AREAS_CIENCIAS]
    return Response(areas, status=status.HTTP_200_OK)


@api_view(['GET'])
def obtener_niveles_educativos(request):
    """Obtener los niveles educativos disponibles."""
    niveles = [{'value': nivel[0], 'label': nivel[1]} for nivel in MateriaCienciasNaturales.NIVELES_EDUCATIVOS]
    return Response(niveles, status=status.HTTP_200_OK)


@api_view(['POST'])
def crear_curso_ciencias(request):
    """Crear un curso de ciencias naturales."""
    user_id = request.data.get('user_id')
    materia_id = request.data.get('materia_id')
    nombre_curso = request.data.get('nombre_curso')
    descripcion_curso = request.data.get('descripcion_curso', '')
    unidades_tematicas = request.data.get('unidades_tematicas', [])
    metodologia = request.data.get('metodologia', '')

    if not all([user_id, materia_id, nombre_curso]):
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(id=user_id)
        if usuario.rol not in ['profesor', 'administrador']:
            return Response({'mensaje': 'No tienes permisos para crear cursos'}, status=status.HTTP_403_FORBIDDEN)

        materia = MateriaCienciasNaturales.objects.get(id=materia_id)

        curso = Curso.objects.create(
            nombre=nombre_curso,
            descripcion=descripcion_curso,
            profesor=usuario if usuario.rol == 'profesor' else None
        )

        CursoCienciasNaturales.objects.create(
            curso=curso,
            materia=materia,
            unidades_tematicas=unidades_tematicas,
            metodologia=metodologia,
            evaluacion_criterios={
                'participacion': 20,
                'tareas': 30,
                'examenes': 50
            }
        )

        return Response({
            'mensaje': 'Curso de ciencias naturales creado exitosamente',
            'curso_id': curso.id,
            'nombre': curso.nombre,
            'materia': materia.nombre,
            'area': materia.get_area_display(),
            'nivel': materia.get_nivel_educativo_display()
        }, status=status.HTTP_201_CREATED)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except MateriaCienciasNaturales.DoesNotExist:
        return Response({'mensaje': 'Materia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def obtener_temas_sugeridos(request):
    """Obtener temas sugeridos basados en el área de ciencias."""
    area = request.GET.get('area', '')

    temas_por_area = {
        'biologia': [
            'Célula y sus componentes',
            'Sistemas del cuerpo humano',
            'Genética básica',
            'Ecosistemas y biodiversidad',
            'Evolución',
            'Fotosíntesis y respiración',
            'Clasificación de seres vivos'
        ],
        'fisica': [
            'Mecánica y movimiento',
            'Fuerzas y energía',
            'Ondas y sonido',
            'Luz y óptica',
            'Electricidad y magnetismo',
            'Calor y temperatura',
            'Astronomía básica'
        ],
        'quimica': [
            'Estructura atómica',
            'Tabla periódica',
            'Enlaces químicos',
            'Reacciones químicas',
            'Estados de la materia',
            'Ácidos y bases',
            'Química orgánica básica'
        ],
        'ciencias_tierra': [
            'Geología y minerales',
            'Placas tectónicas',
            'Ciclo del agua',
            'Clima y meteorología',
            'Recursos naturales',
            'Contaminación ambiental'
        ],
        'astronomia': [
            'Sistema solar',
            'Estrellas y galaxias',
            'Exploración espacial',
            'Fases lunares',
            'Constelaciones'
        ],
        'ecologia': [
            'Cadenas alimentarias',
            'Ciclos biogeoquímicos',
            'Conservación ambiental',
            'Cambio climático',
            'Desarrollo sostenible'
        ]
    }

    temas = temas_por_area.get(area, [])
    return Response({'area': area, 'temas_sugeridos': temas}, status=status.HTTP_200_OK)
