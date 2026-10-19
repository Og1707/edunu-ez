from django.db import models
from apps.usuarios.models import Usuario


class Asignatura(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'api_asignatura'
        ordering = ['nombre']
        verbose_name = 'Asignatura'
        verbose_name_plural = 'Asignaturas'

    def __str__(self):
        return self.nombre


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
    asignaturas = models.ManyToManyField(
        Asignatura,
        blank=True,
        related_name='cursos',
    )

    class Meta:
        db_table = 'api_curso'

    def __str__(self):
        return self.nombre


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
        db_table = 'api_estudiantecurso'
        unique_together = ('estudiante', 'curso')

    def __str__(self):
        return f"{self.estudiante.username} en {self.curso.nombre}"
