from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    ROLES = [
        ('administrador', 'Administrador'),
        ('profesor', 'Profesor'),
        ('estudiante', 'Estudiante'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='estudiante')
    nombre_completo = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"



# Curso
class Curso(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    profesor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'rol': 'profesor'},
        related_name='cursos_asignados'
    )

    def __str__(self):
        return self.nombre


# Relación estudiante-curso
class EstudianteCurso(models.Model):
    estudiante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'estudiante'},
        related_name='cursos'
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='estudiantes'
    )
    fecha_inscripcion = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('estudiante', 'curso')

    def __str__(self):
        return f"{self.estudiante.username} en {self.curso.nombre}"


#activiad
class Actividad(models.Model):
    TIPOS = [
        ('video', 'Video'),
        ('juego', 'Juego Interactivo'),
        ('sopa_letras', 'Sopa de letras'),
        ('crucigrama', 'Crucigrama'),
        ('palabras', 'Juego de palabras'),
        ('lectura_comprensiva', 'Lectura Comprensiva'),
        ('experimento_virtual', 'Experimento Virtual'),
        ('quiz_ciencias', 'Quiz de Ciencias'),
        ('simulador', 'Simulador Educativo'),
        ('laboratorio_virtual', 'Laboratorio Virtual'),
        ('otro', 'Otro'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='otro')
    recurso = models.FileField(
        upload_to='recursos_actividades/',
        null=True,
        blank=True
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_limite = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=[
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('en_revision', 'En Revisión'),
    ], default='pendiente')

    # Actividad pertenece a un curso
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='actividades'
    )

    # Quien creó la actividad (profesor)
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'profesor'},
        related_name='actividades_creadas'
    )

    def __str__(self):
        return f"{self.titulo} ({self.curso.nombre})"



# Modelo de Reporte
class Reporte(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='reportes'
    )
    estudiante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'estudiante'},
        related_name='reportes_estudiante'
    )
    profesor = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'profesor'},
        related_name='reportes_profesor'
    )
    fecha_envio = models.DateTimeField(auto_now_add=True)
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    observaciones = models.TextField(blank=True)
    carencias_detectadas = models.TextField(blank=True)
    recomendaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Reporte de {self.estudiante.username} - {self.actividad.titulo}"

# Modelo específico para Materias de Ciencias Naturales
class MateriaCienciasNaturales(models.Model):
    AREAS_CIENCIAS = [
        ('biologia', 'Biología'),
        ('fisica', 'Física'),
        ('quimica', 'Química'),
        ('ciencias_tierra', 'Ciencias de la Tierra'),
        ('astronomia', 'Astronomía'),
        ('ecologia', 'Ecología'),
    ]
    
    NIVELES_EDUCATIVOS = [
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('bachillerato', 'Bachillerato'),
    ]
    
    nombre = models.CharField(max_length=100)
    area = models.CharField(max_length=20, choices=AREAS_CIENCIAS)
    nivel_educativo = models.CharField(max_length=15, choices=NIVELES_EDUCATIVOS)
    descripcion = models.TextField(blank=True)
    temas_principales = models.JSONField(default=list, help_text="Lista de temas principales de la materia")
    objetivos_aprendizaje = models.TextField(blank=True)
    recursos_recomendados = models.JSONField(default=list, help_text="URLs y recursos educativos recomendados")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Materia de Ciencias Naturales"
        verbose_name_plural = "Materias de Ciencias Naturales"
        unique_together = ('nombre', 'area', 'nivel_educativo')
    
    def __str__(self):
        return f"{self.nombre} - {self.get_area_display()} ({self.get_nivel_educativo_display()})"

# Extender el modelo Curso para incluir materias de ciencias
class CursoCienciasNaturales(models.Model):
    curso = models.OneToOneField(
        Curso,
        on_delete=models.CASCADE,
        related_name='ciencias_naturales'
    )
    materia = models.ForeignKey(
        MateriaCienciasNaturales,
        on_delete=models.CASCADE,
        related_name='cursos'
    )
    unidades_tematicas = models.JSONField(default=list, help_text="Unidades temáticas específicas del curso")
    metodologia = models.TextField(blank=True, help_text="Metodología de enseñanza específica")
    evaluacion_criterios = models.JSONField(default=dict, help_text="Criterios de evaluación específicos")
    
    class Meta:
        verbose_name = "Curso de Ciencias Naturales"
        verbose_name_plural = "Cursos de Ciencias Naturales"
    
    def __str__(self):
        return f"{self.curso.nombre} - {self.materia.nombre}"

# Modelo para asignación de actividades
class AsignacionActividad(models.Model):
    ESTADOS_ASIGNACION = [
        ('asignada', 'Asignada'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('revisada', 'Revisada'),
        ('calificada', 'Calificada'),
    ]
    
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    estudiante = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'estudiante'},
        related_name='actividades_asignadas'
    )
    profesor = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'profesor'},
        related_name='actividades_asignadas_por_mi'
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_ASIGNACION, default='asignada')
    calificacion = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    comentarios_profesor = models.TextField(blank=True, help_text="Comentarios del profesor")
    comentarios_estudiante = models.TextField(blank=True, help_text="Comentarios del estudiante")
    archivo_entrega = models.FileField(
        upload_to='entregas_actividades/',
        null=True,
        blank=True,
        help_text="Archivo de entrega del estudiante"
    )
    
    class Meta:
        verbose_name = "Asignación de Actividad"
        verbose_name_plural = "Asignaciones de Actividades"
        unique_together = ('actividad', 'estudiante')
    
    def __str__(self):
        return f"{self.actividad.titulo} → {self.estudiante.username} (por {self.profesor.username})"

# ========== MODELOS PARA JUEGOS EDUCATIVOS INFANTILES ==========

class CategoriaJuego(models.Model):
    """Categorías de juegos educativos para niños"""
    TIPOS_CATEGORIA = [
        ('matematicas', 'Matemáticas Básicas'),
        ('lenguaje', 'Lenguaje y Lectura'),
        ('ciencias', 'Ciencias Naturales'),
        ('colores_formas', 'Colores y Formas'),
        ('memoria', 'Juegos de Memoria'),
        ('logica', 'Lógica Simple'),
        ('creatividad', 'Creatividad y Arte'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPOS_CATEGORIA)
    descripcion = models.TextField(blank=True)
    edad_minima = models.IntegerField(default=3, help_text="Edad mínima recomendada")
    edad_maxima = models.IntegerField(default=12, help_text="Edad máxima recomendada")
    icono = models.CharField(max_length=50, default='🎮', help_text="Emoji o icono para la categoría")
    activa = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Categoría de Juego"
        verbose_name_plural = "Categorías de Juegos"
    
    def __str__(self):
        return f"{self.icono} {self.nombre}"

class JuegoEducativo(models.Model):
    """Juegos educativos simples para niños"""
    NIVELES_DIFICULTAD = [
        ('muy_facil', 'Muy Fácil (3-5 años)'),
        ('facil', 'Fácil (6-8 años)'),
        ('intermedio', 'Intermedio (9-12 años)'),
    ]
    
    TIPOS_JUEGO = [
        ('memoria_colores', 'Memoria de Colores'),
        ('contar_objetos', 'Contar Objetos'),
        ('formas_geometricas', 'Formas Geométricas'),
        ('colores_primarios', 'Colores Primarios'),
        ('animales_sonidos', 'Animales y Sonidos'),
        ('letras_palabras', 'Letras y Palabras'),
        ('numeros_basicos', 'Números Básicos'),
        ('puzzle_simple', 'Puzzle Simple'),
        ('clasificacion', 'Clasificación de Objetos'),
        ('secuencias', 'Secuencias Lógicas'),
    ]
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.ForeignKey(CategoriaJuego, on_delete=models.CASCADE, related_name='juegos')
    tipo_juego = models.CharField(max_length=30, choices=TIPOS_JUEGO)
    nivel_dificultad = models.CharField(max_length=15, choices=NIVELES_DIFICULTAD, default='facil')
    
    # Configuración del juego (JSON)
    configuracion = models.JSONField(default=dict, help_text="Configuración específica del juego")
    
    # Metadatos educativos
    objetivos_aprendizaje = models.TextField(help_text="Qué aprenderán los niños")
    habilidades_desarrolla = models.JSONField(default=list, help_text="Lista de habilidades que desarrolla")
    
    # Configuración de edad y tiempo
    edad_minima = models.IntegerField(default=3)
    edad_maxima = models.IntegerField(default=12)
    tiempo_estimado = models.IntegerField(default=5, help_text="Tiempo estimado en minutos")
    
    # Estado y metadatos
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Estadísticas
    veces_jugado = models.IntegerField(default=0)
    puntuacion_promedio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Juego Educativo"
        verbose_name_plural = "Juegos Educativos"
        ordering = ['categoria', 'nivel_dificultad', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} ({self.get_nivel_dificultad_display()})"

class PartidaJuego(models.Model):
    """Registro de partidas jugadas por estudiantes"""
    ESTADOS_PARTIDA = [
        ('iniciada', 'Iniciada'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('abandonada', 'Abandonada'),
    ]
    
    juego = models.ForeignKey(JuegoEducativo, on_delete=models.CASCADE, related_name='partidas')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'estudiante'})
    actividad_asignada = models.ForeignKey(AsignacionActividad, on_delete=models.CASCADE, null=True, blank=True)
    
    # Datos de la partida
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADOS_PARTIDA, default='iniciada')
    
    # Resultados
    puntuacion = models.IntegerField(default=0)
    puntuacion_maxima = models.IntegerField(default=100)
    tiempo_jugado = models.IntegerField(default=0, help_text="Tiempo en segundos")
    intentos = models.IntegerField(default=1)
    aciertos = models.IntegerField(default=0)
    errores = models.IntegerField(default=0)
    
    # Datos adicionales del juego
    datos_partida = models.JSONField(default=dict, help_text="Datos específicos de la partida")
    
    class Meta:
        verbose_name = "Partida de Juego"
        verbose_name_plural = "Partidas de Juegos"
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.estudiante.username} - {self.juego.titulo} ({self.puntuacion}/{self.puntuacion_maxima})"
    
    @property
    def porcentaje_aciertos(self):
        total = self.aciertos + self.errores
        return round((self.aciertos / total * 100) if total > 0 else 0, 1)
    
    @property
    def tiempo_formateado(self):
        minutos = self.tiempo_jugado // 60
        segundos = self.tiempo_jugado % 60
        return f"{minutos}:{segundos:02d}"