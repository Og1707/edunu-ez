from django.db.models import Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from api.permissions import IsProfesor
from ..models import CategoriaJuego, JuegoEducativo, Usuario, AsignacionActividad, PartidaJuego


@api_view(['GET'])
def listar_categorias_juegos(request):
    """Listar todas las categorías de juegos disponibles."""
    try:
        categorias = CategoriaJuego.objects.filter(activa=True).order_by('nombre')
        categorias_data = []
        for categoria in categorias:
            categorias_data.append({
                'id': categoria.id,
                'nombre': categoria.nombre,
                'tipo': categoria.tipo,
                'descripcion': categoria.descripcion,
                'edad_minima': categoria.edad_minima,
                'edad_maxima': categoria.edad_maxima,
                'icono': categoria.icono,
                'total_juegos': categoria.juegos.filter(activo=True).count()
            })

        return Response({'categorias': categorias_data, 'total_categorias': len(categorias_data)}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def listar_juegos_educativos(request):
    """Listar juegos educativos con filtros opcionales."""
    categoria_id = request.GET.get('categoria_id')
    nivel_dificultad = request.GET.get('nivel_dificultad')
    edad = request.GET.get('edad')

    try:
        juegos = JuegoEducativo.objects.filter(activo=True)
        if categoria_id:
            juegos = juegos.filter(categoria_id=categoria_id)
        if nivel_dificultad:
            juegos = juegos.filter(nivel_dificultad=nivel_dificultad)
        if edad:
            edad_int = int(edad)
            juegos = juegos.filter(edad_minima__lte=edad_int, edad_maxima__gte=edad_int)

        juegos = juegos.select_related('categoria').order_by('categoria__nombre', 'nivel_dificultad')
        juegos_data = []
        for juego in juegos:
            juegos_data.append({
                'id': juego.id,
                'titulo': juego.titulo,
                'descripcion': juego.descripcion,
                'categoria': {
                    'id': juego.categoria.id,
                    'nombre': juego.categoria.nombre,
                    'icono': juego.categoria.icono
                },
                'tipo_juego': juego.tipo_juego,
                'tipo_juego_display': dict(juego.TIPOS_JUEGO).get(juego.tipo_juego),
                'nivel_dificultad': juego.nivel_dificultad,
                'nivel_dificultad_display': dict(juego.NIVELES_DIFICULTAD).get(juego.nivel_dificultad),
                'edad_minima': juego.edad_minima,
                'edad_maxima': juego.edad_maxima,
                'tiempo_estimado': juego.tiempo_estimado,
                'objetivos_aprendizaje': juego.objetivos_aprendizaje,
                'habilidades_desarrolla': juego.habilidades_desarrolla,
                'veces_jugado': juego.veces_jugado,
                'puntuacion_promedio': float(juego.puntuacion_promedio),
                'configuracion': juego.configuracion
            })

        return Response({
            'juegos': juegos_data,
            'total_juegos': len(juegos_data),
            'filtros_aplicados': {
                'categoria_id': categoria_id,
                'nivel_dificultad': nivel_dificultad,
                'edad': edad
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor])
def crear_juego_educativo(request):
    """Crear un nuevo juego educativo (solo profesores)."""
    profesor = request.user

    try:
        juego_data = {
            'titulo': request.data.get('titulo'),
            'descripcion': request.data.get('descripcion'),
            'categoria_id': request.data.get('categoria_id'),
            'tipo_juego': request.data.get('tipo_juego'),
            'nivel_dificultad': request.data.get('nivel_dificultad', 'facil'),
            'objetivos_aprendizaje': request.data.get('objetivos_aprendizaje'),
            'habilidades_desarrolla': request.data.get('habilidades_desarrolla', []),
            'edad_minima': request.data.get('edad_minima', 3),
            'edad_maxima': request.data.get('edad_maxima', 12),
            'tiempo_estimado': request.data.get('tiempo_estimado', 5),
            'configuracion': request.data.get('configuracion', {}),
            'creado_por': profesor,
        }

        juego = JuegoEducativo.objects.create(**juego_data)
        return Response({
            'mensaje': 'Juego educativo creado exitosamente',
            'juego': {
                'id': juego.id,
                'titulo': juego.titulo,
                'tipo_juego': juego.tipo_juego,
                'nivel_dificultad': juego.nivel_dificultad,
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def iniciar_partida_juego(request):
    """Iniciar una nueva partida de juego para un estudiante."""
    juego_id = request.data.get('juego_id')
    actividad_asignada_id = request.data.get('actividad_asignada_id')
    estudiante = request.user

    if not juego_id:
        return Response({'mensaje': 'Falta juego_id'}, status=status.HTTP_400_BAD_REQUEST)

    if estudiante.rol != 'estudiante':
        return Response({'mensaje': 'Solo los estudiantes pueden jugar'}, status=status.HTTP_403_FORBIDDEN)

    try:
        juego = JuegoEducativo.objects.get(id=juego_id, activo=True)
        actividad_asignada = None
        if actividad_asignada_id:
            actividad_asignada = AsignacionActividad.objects.get(id=actividad_asignada_id, estudiante=estudiante)

        partida = PartidaJuego.objects.create(
            juego=juego,
            estudiante=estudiante,
            actividad_asignada=actividad_asignada,
            estado='iniciada',
        )

        juego.veces_jugado += 1
        juego.save()

        return Response({
            'mensaje': 'Partida iniciada exitosamente',
            'partida': {
                'id': partida.id,
                'juego_titulo': juego.titulo,
                'fecha_inicio': partida.fecha_inicio,
                'configuracion_juego': juego.configuracion,
            }
        }, status=status.HTTP_201_CREATED)
    except JuegoEducativo.DoesNotExist:
        return Response({'mensaje': 'Juego no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except AsignacionActividad.DoesNotExist:
        return Response({'mensaje': 'Actividad asignada no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def finalizar_partida_juego(request):
    """Finalizar una partida y guardar resultados."""
    partida_id = request.data.get('partida_id')
    puntuacion = request.data.get('puntuacion', 0)
    aciertos = request.data.get('aciertos', 0)
    errores = request.data.get('errores', 0)
    tiempo_jugado = request.data.get('tiempo_jugado', 0)
    datos_partida = request.data.get('datos_partida', {})

    if not partida_id:
        return Response({'mensaje': 'ID de partida requerido'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        partida = PartidaJuego.objects.get(id=partida_id)
        partida.estado = 'completada'
        partida.fecha_fin = timezone.now()
        partida.puntuacion = puntuacion
        partida.aciertos = aciertos
        partida.errores = errores
        partida.tiempo_jugado = tiempo_jugado
        partida.datos_partida = datos_partida
        partida.save()

        juego = partida.juego
        partidas_completadas = PartidaJuego.objects.filter(juego=juego, estado='completada')
        if partidas_completadas.exists():
            promedio = partidas_completadas.aggregate(promedio=Avg('puntuacion'))['promedio']
            juego.puntuacion_promedio = promedio or 0
            juego.save()

        return Response({
            'mensaje': 'Partida finalizada exitosamente',
            'resultados': {
                'puntuacion': partida.puntuacion,
                'porcentaje_aciertos': partida.porcentaje_aciertos,
                'tiempo_formateado': partida.tiempo_formateado,
                'estado': 'completada'
            }
        }, status=status.HTTP_200_OK)
    except PartidaJuego.DoesNotExist:
        return Response({'mensaje': 'Partida no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
