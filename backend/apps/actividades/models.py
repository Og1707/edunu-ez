from django.db import models
from apps.core.models import TimeStampedModel, SoftDeleteModel
from apps.usuarios.models import Usuario
from apps.cursos.models import Curso


class Actividad(TimeStampedModel, SoftDeleteModel):
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

    TEMPLATE_TYPES = [
        ('legacy', 'Actividad Antigua'),
        ('multimedia', 'Plantilla Multimedia'),
        ('texto', 'Plantilla Texto'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default='otro')
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPES,
        default='legacy',
        help_text="Tipo de plantilla para esta actividad"
    )
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

    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='actividades'
    )

    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'rol': 'profesor'},
        related_name='actividades_creadas'
    )

    class Meta:
        db_table = 'api_actividad'
        indexes = [
            models.Index(fields=['curso', 'estado'], name='idx_actividad_curso_estado'),
            models.Index(fields=['creado_por', 'created_at'], name='idx_act_creador_fecha'),
        ]

    def __str__(self):
        return f"{self.titulo} ({self.curso.nombre})"


class Reporte(TimeStampedModel):
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

    class Meta:
        db_table = 'api_reporte'

    def __str__(self):
        return f"Reporte de {self.estudiante.username} - {self.actividad.titulo}"


class AsignacionActividad(TimeStampedModel):
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
        db_table = 'api_asignacionactividad'
        verbose_name = "Asignación de Actividad"
        verbose_name_plural = "Asignaciones de Actividades"
        unique_together = ('actividad', 'estudiante')
        indexes = [
            models.Index(fields=['estudiante', 'estado'], name='idx_asig_estudiante_estado'),
            models.Index(fields=['profesor', 'estado'], name='idx_asig_profesor_estado'),
        ]
    
    def __str__(self):
        return f"{self.actividad.titulo} → {self.estudiante.username} (por {self.profesor.username})"
