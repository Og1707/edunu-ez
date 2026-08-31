from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from api.permissions import IsProfesor
from api.services.juegos_service import JuegosService


@api_view(['GET'])
def listar_categorias_juegos(request):
    """Listar todas las categorías de juegos disponibles con caching Redis y consulta anti N+1."""
    categorias_data = JuegosService.listar_categorias_optimizadas()
    return Response(
        {'categorias': categorias_data, 'total_categorias': len(categorias_data)},
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def listar_juegos_educativos(request):
    """Listar juegos educativos con filtros opcionales optimizado con select_related."""
    categoria_id = request.GET.get('categoria_id')
    nivel_dificultad = request.GET.get('nivel_dificultad')
    edad = request.GET.get('edad')

    juegos_data = JuegosService.listar_juegos_optimizados(
        categoria_id=categoria_id,
        nivel_dificultad=nivel_dificultad,
        edad=edad
    )

    return Response({
        'juegos': juegos_data,
        'total_juegos': len(juegos_data),
        'filtros_aplicados': {
            'categoria_id': categoria_id,
            'nivel_dificultad': nivel_dificultad,
            'edad': edad
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor])
def crear_juego_educativo(request):
    """Crear un nuevo juego educativo (solo profesores) con invalidación de caché."""
    juego = JuegosService.crear_juego(profesor=request.user, datos=request.data)
    return Response({
        'mensaje': 'Juego educativo creado exitosamente',
        'juego': {
            'id': juego.id,
            'titulo': juego.titulo,
            'tipo_juego': juego.tipo_juego,
            'nivel_dificultad': juego.nivel_dificultad,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def iniciar_partida_juego(request):
    """Iniciar una nueva partida de juego para un estudiante."""
    juego_id = request.data.get('juego_id')
    actividad_asignada_id = request.data.get('actividad_asignada_id')

    partida_data = JuegosService.iniciar_partida(
        estudiante=request.user,
        juego_id=juego_id,
        actividad_asignada_id=actividad_asignada_id
    )

    return Response({
        'mensaje': 'Partida iniciada exitosamente',
        'partida': partida_data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def finalizar_partida_juego(request):
    """Finalizar una partida y guardar resultados recalculando promedios atómicamente."""
    partida_id = request.data.get('partida_id')
    puntuacion = request.data.get('puntuacion', 0)
    aciertos = request.data.get('aciertos', 0)
    errores = request.data.get('errores', 0)
    tiempo_jugado = request.data.get('tiempo_jugado', 0)
    datos_partida = request.data.get('datos_partida', {})

    resultados = JuegosService.finalizar_partida(
        partida_id=partida_id,
        puntuacion=puntuacion,
        aciertos=aciertos,
        errores=errores,
        tiempo_jugado=tiempo_jugado,
        datos_partida=datos_partida
    )

    return Response({
        'mensaje': 'Partida finalizada exitosamente',
        'resultados': resultados
    }, status=status.HTTP_200_OK)
