from django.db import models
from apps.cursos.models import Curso


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
        db_table = 'api_materiacienciasnaturales'
        verbose_name = "Materia de Ciencias Naturales"
        verbose_name_plural = "Materias de Ciencias Naturales"
        unique_together = ('nombre', 'area', 'nivel_educativo')
    
    def __str__(self):
        return f"{self.nombre} - {self.get_area_display()} ({self.get_nivel_educativo_display()})"


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
        db_table = 'api_cursocienciasnaturales'
        verbose_name = "Curso de Ciencias Naturales"
        verbose_name_plural = "Cursos de Ciencias Naturales"
    
    def __str__(self):
        return f"{self.curso.nombre} - {self.materia.nombre}"
