"""
Servicio de Caché con Redis implementando el patrón Cache-Aside con invalidación por eventos.
Incluye resiliencia y fallback automático a base de datos si Redis no está disponible.
"""

import logging
from typing import Any, Callable, Optional
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheService:
    """
    Servicio centralizado de almacenamiento en caché para catálogos y consultas frecuentes.
    """

    # TTLs en segundos
    TTL_CATALOGOS: int = 3600  # 1 hora para catálogos estáticos
    TTL_LISTADOS: int = 300    # 5 minutos para listados que cambian poco

    # Claves canónicas de caché
    KEY_TIPOS_ACTIVIDAD = "catalogo:tipos_actividad"
    KEY_AREAS_CIENCIAS = "catalogo:areas_ciencias"
    KEY_NIVELES_EDUCATIVOS = "catalogo:niveles_educativos"
    KEY_TEMAS_SUGERIDOS_PREFIX = "catalogo:temas:"
    KEY_CATEGORIAS_JUEGOS = "catalogo:categorias_juegos"
    KEY_CURSOS_PUBLICOS = "catalogo:cursos_publicos"

    @classmethod
    def get(cls, key: str) -> Optional[Any]:
        """Obtiene un valor de caché de forma segura."""
        try:
            return cache.get(key)
        except Exception as exc:
            logger.warning("Error al leer de Redis (key=%s): %s", key, exc)
            return None

    @classmethod
    def set(cls, key: str, value: Any, timeout: int = TTL_CATALOGOS) -> bool:
        """Guarda un valor en caché de forma segura."""
        try:
            cache.set(key, value, timeout=timeout)
            return True
        except Exception as exc:
            logger.warning("Error al escribir en Redis (key=%s): %s", key, exc)
            return False

    @classmethod
    def delete(cls, key: str) -> bool:
        """Elimina una clave específica de la caché."""
        try:
            cache.delete(key)
            logger.info("Caché invalidada para key=%s", key)
            return True
        except Exception as exc:
            logger.warning("Error al eliminar de Redis (key=%s): %s", key, exc)
            return False

    @classmethod
    def get_or_set(cls, key: str, default_factory: Callable[[], Any], timeout: int = TTL_CATALOGOS) -> Any:
        """
        Patrón Cache-Aside: intenta obtener de caché, si no existe o falla,
        ejecuta default_factory(), guarda el resultado y lo retorna.
        """
        cached_value = cls.get(key)
        if cached_value is not None:
            return cached_value

        # Cache Miss o Redis no disponible: calcular valor
        value = default_factory()
        cls.set(key, value, timeout=timeout)
        return value

    # ============= MÉTODOS DE INVALIDACIÓN POR EVENTOS =============

    @classmethod
    def invalidar_categorias_juegos(cls) -> None:
        """Invalida la caché de categorías de juegos al crear/editar categorías."""
        cls.delete(cls.KEY_CATEGORIAS_JUEGOS)

    @classmethod
    def invalidar_cursos(cls) -> None:
        """Invalida la lista pública de cursos al crear o modificar cursos."""
        cls.delete(cls.KEY_CURSOS_PUBLICOS)

    @classmethod
    def invalidar_materias_ciencias(cls) -> None:
        """Invalida catálogos de materias de ciencias."""
        cls.delete(cls.KEY_AREAS_CIENCIAS)
        cls.delete(cls.KEY_NIVELES_EDUCATIVOS)
