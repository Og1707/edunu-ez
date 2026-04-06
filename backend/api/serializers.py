import rest_framework.serializers as serializers
from django.contrib.auth.hashers import make_password
from .models import Usuario, Reporte, Actividad, Curso, EstudianteCurso, AsignacionActividad

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'rol', 'nombre_completo']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        # Hashear la contraseña antes de guardar
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)

class ActividadSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = Actividad
        fields = ['id', 'titulo', 'descripcion', 'tipo', 'recurso', 'fecha_limite', 'estado', 'curso', 'curso_nombre', 'creado_por', 'fecha_creacion']
        read_only_fields = ['creado_por', 'fecha_creacion']
    
    def create(self, validated_data):
        # El usuario que crea la actividad se asigna automáticamente
        request = self.context.get('request')
        if request and request.user:
            validated_data['creado_por'] = request.user
        return super().create(validated_data)

class CursoSerializer(serializers.ModelSerializer):
    profesor_nombre = serializers.CharField(source='profesor.nombre_completo', read_only=True)
    
    class Meta:
        model = Curso
        fields = ['id', 'nombre', 'descripcion', 'profesor', 'profesor_nombre']

class EstudianteCursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstudianteCurso
        fields = ['id', 'estudiante', 'curso', 'fecha_inscripcion']


class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = [
            'id',
            'actividad',
            'estudiante',
            'profesor',
            'fecha_envio',
            'calificacion',
            'observaciones',
            'carencias_detectadas',
            'recomendaciones',
        ]
        read_only_fields = ['fecha_envio']

class AsignacionActividadSerializer(serializers.ModelSerializer):
    actividad_titulo = serializers.CharField(source='actividad.titulo', read_only=True)
    estudiante_nombre = serializers.CharField(source='estudiante.nombre_completo', read_only=True)
    profesor_nombre = serializers.CharField(source='profesor.nombre_completo', read_only=True)
    curso_nombre = serializers.CharField(source='actividad.curso.nombre', read_only=True)
    
    class Meta:
        model = AsignacionActividad
        fields = [
            'id', 'actividad', 'estudiante', 'profesor', 'fecha_asignacion', 
            'fecha_entrega', 'estado', 'calificacion', 'comentarios_profesor', 
            'comentarios_estudiante', 'archivo_entrega', 'actividad_titulo',
            'estudiante_nombre', 'profesor_nombre', 'curso_nombre'
        ]
        read_only_fields = ['fecha_asignacion', 'profesor']
