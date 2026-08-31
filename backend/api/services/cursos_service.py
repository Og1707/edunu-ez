"""
Servicio de negocio para la gestión de cursos, asignación de profesores y materias de ciencias.
Encapsula transacciones atómicas, optimizaciones de consultas y caching con Redis.
"""

import logging
from typing import List, Dict, Any, Optional
from django.db import transaction
from django.db.models import Count

from api.models import Curso, Usuario, MateriaCienciasNaturales, CursoCienciasNaturales
from api.exceptions import (
    ResourceNotFoundException,
    PermissionDeniedBusinessException,
    BusinessValidationException
)
from api.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class CursosService:
    """
    Capa de servicio para cursos y materias de ciencias naturales.
    """

    @classmethod
    def listar_cursos_optimizados(cls) -> List[Dict[str, Any]]:
        """Lista todos los cursos con select_related hacia el profesor y caching en Redis."""
        def _fetch_from_db():
            cursos = Curso.objects.select_related('profesor').all().order_by('nombre')
            return [
                {
                    'id': c.id,
                    'nombre': c.nombre,
                    'descripcion': c.descripcion,
                    'profesor': c.profesor_id,
                    'profesor_nombre': c.profesor.nombre_completo if c.profesor else None,
                }
                for c in cursos
            ]

        return CacheService.get_or_set(
            CacheService.KEY_CURSOS_PUBLICOS,
            _fetch_from_db,
            timeout=CacheService.TTL_LISTADOS
        )

    @classmethod
    @transaction.atomic
    def crear_curso(cls, creador: Usuario, datos: Dict[str, Any]) -> Curso:
        """Crea un curso nuevo y asigna el profesor respetando el rol del creador."""
        nombre = datos.get('nombre')
        if not nombre:
            raise BusinessValidationException("El nombre del curso es obligatorio.", code="NOMBRE_REQUERIDO")

        profesor_id = datos.get('profesor')
        profesor = None

        if creador.rol == 'profesor':
            profesor = creador
        elif creador.rol == 'administrador' and profesor_id:
            try:
                profesor = Usuario.objects.get(id=profesor_id, rol='profesor')
            except Usuario.DoesNotExist:
                raise ResourceNotFoundException("El profesor especificado no existe.", code="PROFESOR_NO_ENCONTRADO")

        curso = Curso.objects.create(
            nombre=nombre,
            descripcion=datos.get('descripcion', ''),
            profesor=profesor
        )

        CacheService.invalidar_cursos()
        return curso

    @classmethod
    @transaction.atomic
    def asignar_profesor(cls, curso_id: int, profesor_id: int) -> Curso:
        """Asigna un profesor a un curso existente."""
        try:
            curso = Curso.objects.get(id=curso_id)
        except Curso.DoesNotExist:
            raise ResourceNotFoundException("Curso no encontrado.", code="CURSO_NO_ENCONTRADO")

        try:
            profesor = Usuario.objects.get(id=profesor_id, rol='profesor')
        except Usuario.DoesNotExist:
            raise ResourceNotFoundException("Profesor no encontrado o no tiene el rol correspondiente.", code="PROFESOR_NO_ENCONTRADO")

        curso.profesor = profesor
        curso.save(update_fields=['profesor'])

        CacheService.invalidar_cursos()
        return curso

    @classmethod
    def listar_materias_ciencias(cls, area: str = '', nivel: str = '') -> List[Dict[str, Any]]:
        """Lista materias de ciencias naturales con total_cursos anotado (sin N+1)."""
        materias = MateriaCienciasNaturales.objects.filter(activa=True).annotate(
            total_cursos_calc=Count('cursos')
        )
        if area:
            materias = materias.filter(area=area)
        if nivel:
            materias = materias.filter(nivel_educativo=nivel)

        materias = materias.order_by('area', 'nivel_educativo', 'nombre')

        return [
            {
                'id': m.id,
                'nombre': m.nombre,
                'area': m.area,
                'area_display': m.get_area_display(),
                'nivel_educativo': m.nivel_educativo,
                'nivel_display': m.get_nivel_educativo_display(),
                'descripcion': m.descripcion,
                'temas_principales': m.temas_principales,
                'objetivos_aprendizaje': m.objetivos_aprendizaje,
                'recursos_recomendados': m.recursos_recomendados,
                'fecha_creacion': m.fecha_creacion,
                'total_cursos': m.total_cursos_calc,
            }
            for m in materias
        ]

    @classmethod
    @transaction.atomic
    def crear_curso_ciencias(cls, usuario: Usuario, datos: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un curso vinculado a una materia de ciencias naturales de manera atómica."""
        materia_id = datos.get('materia_id')
        nombre_curso = datos.get('nombre_curso')

        if not materia_id or not nombre_curso:
            raise BusinessValidationException("Faltan datos requeridos (materia_id o nombre_curso).", code="DATOS_INCOMPLETOS")

        try:
            materia = MateriaCienciasNaturales.objects.get(id=materia_id)
        except MateriaCienciasNaturales.DoesNotExist:
            raise ResourceNotFoundException("Materia de ciencias no encontrada.", code="MATERIA_NO_ENCONTRADA")

        curso = Curso.objects.create(
            nombre=nombre_curso,
            descripcion=datos.get('descripcion_curso', ''),
            profesor=usuario if usuario.rol == 'profesor' else None
        )

        curso_ciencias = CursoCienciasNaturales.objects.create(
            curso=curso,
            materia=materia,
            unidades_tematicas=datos.get('unidades_tematicas', []),
            metodologia=datos.get('metodologia', ''),
            evaluacion_criterios={
                'participacion': 20,
                'tareas': 30,
                'examenes': 50
            }
        )

        CacheService.invalidar_cursos()

        return {
            'mensaje': 'Curso de ciencias naturales creado exitosamente',
            'curso_id': curso.id,
            'nombre': curso.nombre,
            'materia': materia.nombre,
            'area': materia.get_area_display(),
            'nivel': materia.get_nivel_educativo_display()
        }

    # ============= MÉTODOS DE CATÁLOGOS CON CACHÉ =============

    @classmethod
    def obtener_areas_ciencias(cls) -> List[Dict[str, str]]:
        """Retorna las áreas de ciencias naturales cacheadas con Redis."""
        def _get():
            return [{'value': a[0], 'label': a[1]} for a in MateriaCienciasNaturales.AREAS_CIENCIAS]

        return CacheService.get_or_set(CacheService.KEY_AREAS_CIENCIAS, _get, timeout=CacheService.TTL_CATALOGOS)

    @classmethod
    def obtener_niveles_educativos(cls) -> List[Dict[str, str]]:
        """Retorna los niveles educativos cacheados con Redis."""
        def _get():
            return [{'value': n[0], 'label': n[1]} for n in MateriaCienciasNaturales.NIVELES_EDUCATIVOS]

        return CacheService.get_or_set(CacheService.KEY_NIVELES_EDUCATIVOS, _get, timeout=CacheService.TTL_CATALOGOS)

    @classmethod
    def obtener_temas_sugeridos(cls, area: str) -> List[str]:
        """Retorna los temas sugeridos para un área de ciencias con caché."""
        cache_key = f"{CacheService.KEY_TEMAS_SUGERIDOS_PREFIX}{area}"

        def _get():
            temas_por_area = {
                'biologia': [
                    'Célula y sus componentes', 'Sistemas del cuerpo humano', 'Genética básica',
                    'Ecosistemas y biodiversidad', 'Evolución', 'Fotosíntesis y respiración',
                    'Clasificación de seres vivos'
                ],
                'fisica': [
                    'Mecánica y movimiento', 'Fuerzas y energía', 'Ondas y sonido',
                    'Luz y óptica', 'Electricidad y magnetismo', 'Calor y temperatura',
                    'Astronomía básica'
                ],
                'quimica': [
                    'Estructura atómica', 'Tabla periódica', 'Enlaces químicos',
                    'Reacciones químicas', 'Estados de la materia', 'Ácidos y bases',
                    'Química orgánica básica'
                ],
                'ciencias_tierra': [
                    'Geología y minerales', 'Placas tectónicas', 'Ciclo del agua',
                    'Clima y meteorología', 'Recursos naturales', 'Contaminación ambiental'
                ],
                'astronomia': [
                    'Sistema solar', 'Estrellas y galaxias', 'Exploración espacial',
                    'Fases lunares', 'Constelaciones'
                ],
                'ecologia': [
                    'Cadenas alimentarias', 'Ciclos biogeoquímicos', 'Conservación ambiental',
                    'Cambio climático', 'Desarrollo sostenible'
                ]
            }
            return temas_por_area.get(area, [])

        return CacheService.get_or_set(cache_key, _get, timeout=CacheService.TTL_CATALOGOS)
