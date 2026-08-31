import pytest
from django.test import RequestFactory
from django.urls import reverse
from rest_framework.test import APIClient

from api.models import Usuario, Curso, Actividad, CategoriaJuego, JuegoEducativo, PartidaJuego, MateriaCienciasNaturales, EstudianteCurso, AsignacionActividad
from api.services.actividades_service import ActividadesService
from api.services.juegos_service import JuegosService
from api.services.cursos_service import CursosService
from api.services.cache_service import CacheService
from api.exceptions import (
    ResourceNotFoundException,
    BusinessValidationException,
    PermissionDeniedBusinessException,
    ConflictBusinessException,
)
from api.middleware.request_logging_middleware import RequestLoggingMiddleware


@pytest.fixture
def profesor(db):
    return Usuario.objects.create_user(
        username='profe_test',
        email='profe@test.com',
        password='password123',
        rol='profesor',
        nombre_completo='Profesor Test'
    )


@pytest.fixture
def estudiante(db):
    return Usuario.objects.create_user(
        username='estudiante_test',
        email='estudiante@test.com',
        password='password123',
        rol='estudiante',
        nombre_completo='Estudiante Test'
    )


@pytest.fixture
def admin_user(db):
    return Usuario.objects.create_user(
        username='admin_test',
        email='admin@test.com',
        password='password123',
        rol='administrador',
        nombre_completo='Admin Test'
    )


@pytest.fixture
def curso_con_estudiante(db, profesor, estudiante):
    curso = Curso.objects.create(nombre='Curso Ciencias 101', profesor=profesor)
    EstudianteCurso.objects.create(curso=curso, estudiante=estudiante)
    return curso


@pytest.fixture
def categoria_juego(db):
    return CategoriaJuego.objects.create(
        nombre='Biología Marina',
        tipo='memoria',
        descripcion='Juegos sobre vida marina',
        activa=True
    )


# =====================================================================
# PRUEBAS DE CACHE SERVICE (TASK 2.3)
# =====================================================================

@pytest.mark.django_db
class TestCacheService:
    def test_cache_get_or_set_and_invalidation(self):
        key = "test_key_cache_aside"
        call_count = 0

        def data_loader():
            nonlocal call_count
            call_count += 1
            return ["dato1", "dato2"]

        # Primer llamado: Cache Miss -> ejecuta factory
        val1 = CacheService.get_or_set(key, data_loader, timeout=60)
        assert val1 == ["dato1", "dato2"]
        assert call_count == 1

        # Segundo llamado: Cache Hit -> no ejecuta factory
        val2 = CacheService.get_or_set(key, data_loader, timeout=60)
        assert val2 == ["dato1", "dato2"]
        assert call_count == 1

        # Invalidar
        CacheService.delete(key)
        val3 = CacheService.get_or_set(key, data_loader, timeout=60)
        assert val3 == ["dato1", "dato2"]
        assert call_count == 2


# =====================================================================
# PRUEBAS DE ACTIVIDADES SERVICE (TASK 2.1 & 2.2)
# =====================================================================

@pytest.mark.django_db
class TestActividadesService:
    def test_asignar_y_obtener_actividades_profesor_optimizadas(self, profesor, estudiante, curso_con_estudiante):
        actividad = Actividad.objects.create(
            titulo='Actividad Celular',
            tipo='quiz_ciencias',
            curso=curso_con_estudiante,
            creado_por=profesor
        )

        # Asignar actividad al curso
        res = ActividadesService.asignar_actividad_a_curso(
            profesor=profesor,
            curso_id=curso_con_estudiante.id,
            actividad_ids=[actividad.id]
        )
        assert len(res['nuevas_asignaciones']) == 1

        # Obtener actividades con estadísticas
        actividades_data = ActividadesService.obtener_actividades_profesor_optimizadas(profesor)
        assert len(actividades_data) == 1
        assert actividades_data[0]['titulo'] == 'Actividad Celular'
        assert actividades_data[0]['estadisticas']['total_estudiantes'] == 1
        assert actividades_data[0]['estadisticas']['total_asignaciones'] == 1

    def test_ciclo_iniciar_y_completar_actividad(self, profesor, estudiante, curso_con_estudiante):
        actividad = Actividad.objects.create(
            titulo='Examen de Fotosíntesis',
            tipo='quiz_ciencias',
            curso=curso_con_estudiante,
            creado_por=profesor
        )

        # 1. Iniciar
        res_ini = ActividadesService.iniciar_actividad(estudiante=estudiante, actividad_id=actividad.id)
        assert res_ini['progreso']['estado'] == 'en_progreso'

        # 2. Completar
        res_comp = ActividadesService.completar_actividad(
            estudiante=estudiante,
            actividad_id=actividad.id,
            puntuacion=95.0,
            tiempo_empleado=12,
            respuestas_detalle=[{'pregunta_id': 1, 'correcta': True}]
        )
        assert res_comp['progreso']['completada'] is True
        assert res_comp['progreso']['puntuacion'] == 95.0

    def test_inscribir_y_remover_estudiante_curso(self, profesor, admin_user, estudiante):
        curso = Curso.objects.create(nombre='Física Mecánica', profesor=profesor)

        # Inscribir
        inscripcion = ActividadesService.inscribir_estudiante_curso(
            user_solicitante=profesor,
            curso_id=curso.id,
            estudiante_id=estudiante.id
        )
        assert inscripcion.estudiante == estudiante
        assert inscripcion.curso == curso

        # Conflicto al re-inscribir
        with pytest.raises(ConflictBusinessException):
            ActividadesService.inscribir_estudiante_curso(
                user_solicitante=profesor,
                curso_id=curso.id,
                estudiante_id=estudiante.id
            )

        # Remover
        ActividadesService.remover_estudiante_curso(user_solicitante=profesor, inscripcion_id=inscripcion.id)
        assert not EstudianteCurso.objects.filter(id=inscripcion.id).exists()


# =====================================================================
# PRUEBAS DE JUEGOS SERVICE (TASK 2.1 & 2.2)
# =====================================================================

@pytest.mark.django_db
class TestJuegosService:
    def test_crear_listar_e_iniciar_partida(self, profesor, estudiante, categoria_juego):
        # Crear juego
        juego = JuegosService.crear_juego(
            profesor=profesor,
            datos={
                'titulo': 'Memoria Celular',
                'descripcion': 'Empareja los organelos',
                'categoria_id': categoria_juego.id,
                'tipo_juego': 'memoria',
                'nivel_dificultad': 'medio'
            }
        )
        assert juego.id is not None
        assert juego.titulo == 'Memoria Celular'

        # Listar con select_related
        juegos = JuegosService.listar_juegos_optimizados(categoria_id=str(categoria_juego.id))
        assert len(juegos) == 1
        assert juegos[0]['categoria']['nombre'] == 'Biología Marina'

        # Iniciar partida
        partida_info = JuegosService.iniciar_partida(estudiante=estudiante, juego_id=juego.id)
        assert partida_info['id'] is not None

        # Finalizar partida y verificar recálculo de promedio
        res_fin = JuegosService.finalizar_partida(
            partida_id=partida_info['id'],
            puntuacion=100.0,
            aciertos=10,
            errores=0,
            tiempo_jugado=45
        )
        assert res_fin['puntuacion'] == 100.0
        juego.refresh_from_db()
        assert float(juego.puntuacion_promedio) == 100.0


# =====================================================================
# PRUEBAS DE CURSOS SERVICE (TASK 2.1 & 2.3)
# =====================================================================

@pytest.mark.django_db
class TestCursosService:
    def test_crear_y_listar_cursos_con_cache(self, profesor):
        curso = CursosService.crear_curso(
            creador=profesor,
            datos={'nombre': 'Química Orgánica Avanzada', 'descripcion': 'Curso avanzado'}
        )
        assert curso.profesor == profesor

        cursos = CursosService.listar_cursos_optimizados()
        assert any(c['nombre'] == 'Química Orgánica Avanzada' for c in cursos)

    def test_catalogos_ciencias_cacheados(self):
        areas = CursosService.obtener_areas_ciencias()
        assert len(areas) > 0

        niveles = CursosService.obtener_niveles_educativos()
        assert len(niveles) > 0

        temas_bio = CursosService.obtener_temas_sugeridos('biologia')
        assert 'Célula y sus componentes' in temas_bio


# =====================================================================
# PRUEBAS DE LOGGING MIDDLEWARE (TASK 2.4)
# =====================================================================

@pytest.mark.django_db
class TestRequestLoggingMiddleware:
    def test_middleware_injects_x_request_id(self, rf, estudiante):
        request = rf.get('/api/cursos/')
        request.user = estudiante

        middleware = RequestLoggingMiddleware(lambda req: APIClient().get('/api/cursos/'))
        response = middleware(request)

        assert 'X-Request-ID' in response
        assert response['X-Request-ID'] == request.request_id
