"""
Servicio de negocio para la gestión de juegos educativos y partidas de estudiantes.
Encapsula transacciones atómicas, agregaciones optimizadas e invalidación de caché.
"""

import logging
from typing import Dict, Any, Optional, List
from django.db import transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone

from api.models import CategoriaJuego, JuegoEducativo, PartidaJuego, AsignacionActividad, Usuario
from api.exceptions import (
    ResourceNotFoundException,
    PermissionDeniedBusinessException,
    BusinessValidationException
)
from api.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class JuegosService:
    """
    Capa de servicio para la lógica de juegos educativos y partidas.
    """

    @classmethod
    def listar_categorias_optimizadas(cls) -> List[Dict[str, Any]]:
        """
        Lista categorías activas con total de juegos anotado (sin N+1) usando caché Redis.
        """
        def _fetch_from_db():
            categorias = (
                CategoriaJuego.objects
                .filter(activa=True)
                .annotate(total_juegos_calc=Count('juegos', filter=Q(juegos__activo=True)))
                .order_by('nombre')
            )
            return [
                {
                    'id': cat.id,
                    'nombre': cat.nombre,
                    'tipo': cat.tipo,
                    'descripcion': cat.descripcion,
                    'edad_minima': cat.edad_minima,
                    'edad_maxima': cat.edad_maxima,
                    'icono': cat.icono,
                    'total_juegos': cat.total_juegos_calc,
                }
                for cat in categorias
            ]

        return CacheService.get_or_set(
            CacheService.KEY_CATEGORIAS_JUEGOS,
            _fetch_from_db,
            timeout=CacheService.TTL_CATALOGOS
        )

    @classmethod
    def listar_juegos_optimizados(
        cls,
        categoria_id: Optional[str] = None,
        nivel_dificultad: Optional[str] = None,
        edad: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista juegos educativos aplicando filtros y cargando la categoría con select_related.
        """
        juegos = JuegoEducativo.objects.filter(activo=True).select_related('categoria')

        if categoria_id:
            juegos = juegos.filter(categoria_id=categoria_id)
        if nivel_dificultad:
            juegos = juegos.filter(nivel_dificultad=nivel_dificultad)
        if edad:
            try:
                edad_int = int(edad)
                juegos = juegos.filter(edad_minima__lte=edad_int, edad_maxima__gte=edad_int)
            except ValueError:
                raise BusinessValidationException("El parámetro edad debe ser un número entero.", code="EDAD_INVALIDA")

        juegos = juegos.order_by('categoria__nombre', 'nivel_dificultad')

        return [
            {
                'id': juego.id,
                'titulo': juego.titulo,
                'descripcion': juego.descripcion,
                'categoria': {
                    'id': juego.categoria.id,
                    'nombre': juego.categoria.nombre,
                    'icono': juego.categoria.icono,
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
                'configuracion': juego.configuracion,
            }
            for juego in juegos
        ]

    @classmethod
    @transaction.atomic
    def crear_juego(cls, profesor: Usuario, datos: Dict[str, Any]) -> JuegoEducativo:
        """Crea un nuevo juego educativo e invalida la caché de categorías."""
        categoria_id = datos.get('categoria_id')
        if not categoria_id:
            raise BusinessValidationException("Falta categoria_id para crear el juego.", code="CATEGORIA_REQUERIDA")

        if not CategoriaJuego.objects.filter(id=categoria_id).exists():
            raise ResourceNotFoundException("La categoría especificada no existe.", code="CATEGORIA_NO_ENCONTRADA")

        juego = JuegoEducativo.objects.create(
            titulo=datos.get('titulo'),
            descripcion=datos.get('descripcion') or '',
            categoria_id=categoria_id,
            tipo_juego=datos.get('tipo_juego'),
            nivel_dificultad=datos.get('nivel_dificultad', 'facil'),
            objetivos_aprendizaje=datos.get('objetivos_aprendizaje') or '',
            habilidades_desarrolla=datos.get('habilidades_desarrolla', []),
            edad_minima=datos.get('edad_minima', 3),
            edad_maxima=datos.get('edad_maxima', 12),
            tiempo_estimado=datos.get('tiempo_estimado', 5),
            configuracion=datos.get('configuracion', {}),
            creado_por=profesor,
        )

        # Invalidar caché de categorías para reflejar nuevo juego
        CacheService.invalidar_categorias_juegos()

        return juego

    @classmethod
    @transaction.atomic
    def iniciar_partida(
        cls, estudiante: Usuario, juego_id: int, actividad_asignada_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Inicia una partida de juego y actualiza el contador de veces jugado."""
        if not juego_id:
            raise BusinessValidationException("Falta juego_id.", code="JUEGO_ID_FALTANTE")

        if estudiante.rol != 'estudiante':
            raise PermissionDeniedBusinessException("Solo los estudiantes pueden jugar.", code="NO_ESTUDIANTE")

        try:
            juego = JuegoEducativo.objects.get(id=juego_id, activo=True)
        except JuegoEducativo.DoesNotExist:
            raise ResourceNotFoundException("Juego no encontrado o inactivo.", code="JUEGO_NO_ENCONTRADO")

        actividad_asignada = None
        if actividad_asignada_id:
            try:
                actividad_asignada = AsignacionActividad.objects.get(id=actividad_asignada_id, estudiante=estudiante)
            except AsignacionActividad.DoesNotExist:
                raise ResourceNotFoundException("Actividad asignada no encontrada.", code="ASIGNACION_NO_ENCONTRADA")

        partida = PartidaJuego.objects.create(
            juego=juego,
            estudiante=estudiante,
            actividad_asignada=actividad_asignada,
            estado='iniciada',
        )

        juego.veces_jugado += 1
        juego.save(update_fields=['veces_jugado'])

        return {
            'id': partida.id,
            'juego_titulo': juego.titulo,
            'fecha_inicio': partida.fecha_inicio,
            'configuracion_juego': juego.configuracion,
        }

    @classmethod
    @transaction.atomic
    def finalizar_partida(
        cls,
        partida_id: int,
        puntuacion: float = 0,
        aciertos: int = 0,
        errores: int = 0,
        tiempo_jugado: int = 0,
        datos_partida: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Finaliza una partida, persiste métricas y recalcula el promedio del juego."""
        if not partida_id:
            raise BusinessValidationException("ID de partida requerido.", code="PARTIDA_ID_FALTANTE")

        try:
            partida = PartidaJuego.objects.select_related('juego').get(id=partida_id)
        except PartidaJuego.DoesNotExist:
            raise ResourceNotFoundException("Partida no encontrada.", code="PARTIDA_NO_ENCONTRADA")

        partida.estado = 'completada'
        partida.fecha_fin = timezone.now()
        partida.puntuacion = puntuacion
        partida.aciertos = aciertos
        partida.errores = errores
        partida.tiempo_jugado = tiempo_jugado
        partida.datos_partida = datos_partida or {}
        partida.save()

        # Recalcular promedio de puntuación del juego atómicamente
        juego = partida.juego
        partidas_completadas = PartidaJuego.objects.filter(juego=juego, estado='completada')
        if partidas_completadas.exists():
            promedio = partidas_completadas.aggregate(promedio=Avg('puntuacion'))['promedio']
            juego.puntuacion_promedio = promedio or 0
            juego.save(update_fields=['puntuacion_promedio'])

        return {
            'puntuacion': partida.puntuacion,
            'porcentaje_aciertos': partida.porcentaje_aciertos,
            'tiempo_formateado': partida.tiempo_formateado,
            'estado': 'completada',
        }
