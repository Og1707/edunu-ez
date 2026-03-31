from django.urls import path
from .views.auth import (
    registrar_usuario,
    login_usuario,
    listar_usuarios_por_rol,
    crear_usuario_con_permisos,
    gestionar_usuario_especifico,
    gestionar_perfil_propio,
)
from .views.cursos import (
    listar_cursos,
    crear_curso,
    gestionar_curso_especifico,
    asignar_profesor_a_curso,
    gestionar_materias_ciencias,
    obtener_areas_ciencias,
    obtener_niveles_educativos,
    crear_curso_ciencias,
    obtener_temas_sugeridos,
)
from .views.actividades import (
    gestionar_actividades,
    obtener_tipos_actividad,
    obtener_actividades_profesor,
    asignar_actividad_curso,
    listar_estudiantes_curso,
    actividades_asignadas_estudiante,
    actividades_curso_profesor,
    obtener_actividades_estudiante,
    iniciar_actividad_estudiante,
    completar_actividad_estudiante,
    obtener_estadisticas_estudiante,
    gestionar_actividad_especifica,
    agregar_estudiante_a_curso,
    remover_estudiante_de_curso,
)
from .views.juegos import (
    listar_categorias_juegos,
    listar_juegos_educativos,
    crear_juego_educativo,
    iniciar_partida_juego,
    finalizar_partida_juego,
)
from .views.wikipedia import (
    obtener_contenido_wikipedia,
    buscar_temas_ciencias,
    generar_actividad_wikipedia,
)
from .views.webhooks import recipientwebhooks


urlpatterns = [
    path('registro/', registrar_usuario, name='registro_usuario'),
    path('login/', login_usuario, name='login_usuario'),
    path('webhook/', recipientwebhooks.as_view(), name='recipient_webhook'),
    path('actividades/', gestionar_actividades, name='gestionar_actividades'),
    path('actividades/profesor/', obtener_actividades_profesor, name='obtener_actividades_profesor'),
    path('cursos/', listar_cursos, name='listar_cursos'),
    path('cursos/crear/', crear_curso, name='crear_curso'),
    path('tipos-actividad/', obtener_tipos_actividad, name='tipos_actividad'),
    # Nuevos endpoints para Wikipedia API
    path('wikipedia/contenido/', obtener_contenido_wikipedia, name='wikipedia_contenido'),
    path('wikipedia/buscar/', buscar_temas_ciencias, name='buscar_temas_ciencias'),
    path('wikipedia/generar-actividad/', generar_actividad_wikipedia, name='generar_actividad_wikipedia'),
    # Endpoints para Ciencias Naturales
    path('ciencias/materias/', gestionar_materias_ciencias, name='gestionar_materias_ciencias'),
    path('ciencias/areas/', obtener_areas_ciencias, name='obtener_areas_ciencias'),
    path('ciencias/niveles/', obtener_niveles_educativos, name='obtener_niveles_educativos'),
    path('ciencias/cursos/crear/', crear_curso_ciencias, name='crear_curso_ciencias'),
    path('ciencias/temas-sugeridos/', obtener_temas_sugeridos, name='obtener_temas_sugeridos'),
    # Endpoints para asignación de actividades
    path('asignar-actividad-curso/', asignar_actividad_curso, name='asignar_actividad_curso'),
    path('estudiantes-curso/', listar_estudiantes_curso, name='listar_estudiantes_curso'),
    path('mis-actividades/', actividades_asignadas_estudiante, name='actividades_asignadas_estudiante'),
    path('actividades-curso-profesor/', actividades_curso_profesor, name='actividades_curso_profesor'),
    # Endpoints para juegos educativos
    path('juegos/categorias/', listar_categorias_juegos, name='listar_categorias_juegos'),
    path('juegos/listar/', listar_juegos_educativos, name='listar_juegos_educativos'),
    path('juegos/crear/', crear_juego_educativo, name='crear_juego_educativo'),
    path('juegos/iniciar-partida/', iniciar_partida_juego, name='iniciar_partida_juego'),
    path('juegos/finalizar-partida/', finalizar_partida_juego, name='finalizar_partida_juego'),
    
    # ============= SISTEMA DE PERMISOS POR ROL =============
    
    # Gestión de usuarios (Profesor: solo estudiantes, Administrador: todos)
    path('usuarios/listar/', listar_usuarios_por_rol, name='listar_usuarios_por_rol'),
    path('usuarios/crear/', crear_usuario_con_permisos, name='crear_usuario_con_permisos'),
    path('usuarios/<int:user_id>/gestionar/', gestionar_usuario_especifico, name='gestionar_usuario_especifico'),
    
    # Gestión de cursos con permisos
    path('cursos/<int:curso_id>/gestionar/', gestionar_curso_especifico, name='gestionar_curso_especifico'),
    path('cursos/<int:curso_id>/asignar-profesor/', asignar_profesor_a_curso, name='asignar_profesor_curso'),
    
    # Gestión de actividades con permisos
    path('actividades/<int:actividad_id>/gestionar/', gestionar_actividad_especifica, name='gestionar_actividad_especifica'),
    
    # Gestión de estudiantes en cursos
    path('estudiantes-curso/agregar/', agregar_estudiante_a_curso, name='agregar_estudiante_curso'),
    path('estudiantes-curso/<int:inscripcion_id>/remover/', remover_estudiante_de_curso, name='remover_estudiante_curso'),
    
    # Perfil de usuario
    path('perfil/gestionar/', gestionar_perfil_propio, name='gestionar_perfil_propio'),
    
    # ============= SISTEMA DE ACTIVIDADES PARA ESTUDIANTES =============
    
    # Actividades del estudiante
    path('estudiante/actividades/', obtener_actividades_estudiante, name='obtener_actividades_estudiante'),
    path('estudiante/actividades/iniciar/', iniciar_actividad_estudiante, name='iniciar_actividad_estudiante'),
    path('estudiante/actividades/completar/', completar_actividad_estudiante, name='completar_actividad_estudiante'),
    path('estudiante/estadisticas/', obtener_estadisticas_estudiante, name='obtener_estadisticas_estudiante'),
]