# Facade / Re-exportación de modelos para mantener retrocompatibilidad total con api.models
from apps.usuarios.models import Usuario
from apps.cursos.models import Curso, EstudianteCurso
from apps.actividades.models import Actividad, Reporte, AsignacionActividad
from apps.plantillas.models import ActividadMultimedia, ActividadTexto, Pregunta, OpcionRespuesta
from apps.juegos.models import CategoriaJuego, JuegoEducativo, PartidaJuego
from apps.ciencias.models import MateriaCienciasNaturales, CursoCienciasNaturales

__all__ = [
    'Usuario',
    'Curso',
    'EstudianteCurso',
    'Actividad',
    'Reporte',
    'AsignacionActividad',
    'ActividadMultimedia',
    'ActividadTexto',
    'Pregunta',
    'OpcionRespuesta',
    'CategoriaJuego',
    'JuegoEducativo',
    'PartidaJuego',
    'MateriaCienciasNaturales',
    'CursoCienciasNaturales',
]