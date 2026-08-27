from django.db import models
from apps.actividades.models import Actividad


class ActividadMultimedia(models.Model):
    TIPOS_ARCHIVO = [
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('imagen', 'Imagen'),
    ]
    
    actividad = models.OneToOneField(
        Actividad,
        on_delete=models.CASCADE,
        related_name='multimedia',
        help_text="Referencia a la actividad base"
    )
    archivo_url_cloudinary = models.URLField(
        max_length=500,
        help_text="URL del archivo alojado en Cloudinary"
    )
    tipo_archivo = models.CharField(
        max_length=20,
        choices=TIPOS_ARCHIVO,
        default='video',
        help_text="Tipo de archivo multimedia"
    )
    duracion_segundos = models.IntegerField(
        null=True,
        blank=True,
        help_text="Duración en segundos (para videos y audios)"
    )
    tamaño_bytes = models.BigIntegerField(
        null=True,
        blank=True,
        help_text="Tamaño del archivo en bytes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_actividadmultimedia'
        verbose_name = "Actividad Multimedia"
        verbose_name_plural = "Actividades Multimedia"
    
    def __str__(self):
        return f"Multimedia - {self.actividad.titulo}"


class ActividadTexto(models.Model):
    actividad = models.OneToOneField(
        Actividad,
        on_delete=models.CASCADE,
        related_name='texto',
        help_text="Referencia a la actividad base"
    )
    tiempo_limite_minutos = models.IntegerField(
        null=True,
        blank=True,
        help_text="Límite de tiempo en minutos. NULL = sin límite"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_actividadtexto'
        verbose_name = "Actividad Texto"
        verbose_name_plural = "Actividades Texto"
    
    def __str__(self):
        return f"Texto - {self.actividad.titulo}"


class Pregunta(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='preguntas',
        help_text="Actividad a la que pertenece esta pregunta"
    )
    enunciado = models.TextField(
        help_text="Texto de la pregunta"
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden de presentación de la pregunta"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_pregunta'
        verbose_name = "Pregunta"
        verbose_name_plural = "Preguntas"
        ordering = ['orden']
        indexes = [
            models.Index(fields=['actividad', 'orden']),
        ]
    
    def __str__(self):
        return f"Q{self.orden}: {self.enunciado[:50]}..."
    
    def tiene_respuesta_correcta(self):
        return self.opciones.filter(es_correcta=True).exists()


class OpcionRespuesta(models.Model):
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        related_name='opciones',
        help_text="Pregunta a la que pertenece esta opción"
    )
    texto = models.TextField(
        help_text="Texto de la opción de respuesta"
    )
    es_correcta = models.BooleanField(
        default=False,
        help_text="Marca si esta es la opción correcta"
    )
    orden = models.PositiveIntegerField(
        default=0,
        help_text="Orden de presentación de la opción"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_opcionrespuesta'
        verbose_name = "Opción de Respuesta"
        verbose_name_plural = "Opciones de Respuesta"
        ordering = ['orden']
        indexes = [
            models.Index(fields=['pregunta', 'orden']),
            models.Index(fields=['es_correcta']),
        ]
    
    def __str__(self):
        marca = "✓" if self.es_correcta else "✗"
        return f"{marca} {self.texto[:50]}..."
