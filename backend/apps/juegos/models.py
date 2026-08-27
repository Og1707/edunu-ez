from django.db import models
from apps.usuarios.models import Usuario
from apps.actividades.models import AsignacionActividad


class CategoriaJuego(models.Model):
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
        db_table = 'api_categoriajuego'
        verbose_name = "Categoría de Juego"
        verbose_name_plural = "Categorías de Juegos"
    
    def __str__(self):
        return f"{self.icono} {self.nombre}"


class JuegoEducativo(models.Model):
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
    
    configuracion = models.JSONField(default=dict, help_text="Configuración específica del juego")
    objetivos_aprendizaje = models.TextField(help_text="Qué aprenderán los niños")
    habilidades_desarrolla = models.JSONField(default=list, help_text="Lista de habilidades que desarrolla")
    
    edad_minima = models.IntegerField(default=3)
    edad_maxima = models.IntegerField(default=12)
    tiempo_estimado = models.IntegerField(default=5, help_text="Tiempo estimado en minutos")
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    veces_jugado = models.IntegerField(default=0)
    puntuacion_promedio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    class Meta:
        db_table = 'api_juegoeducativo'
        verbose_name = "Juego Educativo"
        verbose_name_plural = "Juegos Educativos"
        ordering = ['categoria', 'nivel_dificultad', 'titulo']
    
    def __str__(self):
        return f"{self.titulo} ({self.get_nivel_dificultad_display()})"


class PartidaJuego(models.Model):
    ESTADOS_PARTIDA = [
        ('iniciada', 'Iniciada'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('abandonada', 'Abandonada'),
    ]
    
    juego = models.ForeignKey(JuegoEducativo, on_delete=models.CASCADE, related_name='partidas')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, limit_choices_to={'rol': 'estudiante'})
    actividad_asignada = models.ForeignKey(AsignacionActividad, on_delete=models.CASCADE, null=True, blank=True)
    
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=15, choices=ESTADOS_PARTIDA, default='iniciada')
    
    puntuacion = models.IntegerField(default=0)
    puntuacion_maxima = models.IntegerField(default=100)
    tiempo_jugado = models.IntegerField(default=0, help_text="Tiempo en segundos")
    intentos = models.IntegerField(default=1)
    aciertos = models.IntegerField(default=0)
    errores = models.IntegerField(default=0)
    
    datos_partida = models.JSONField(default=dict, help_text="Datos específicos de la partida")
    
    class Meta:
        db_table = 'api_partidajuego'
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
