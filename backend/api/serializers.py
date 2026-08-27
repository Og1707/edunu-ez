import rest_framework.serializers as serializers
from django.contrib.auth.hashers import make_password
from .models import (
    Usuario, Reporte, Actividad, Curso, EstudianteCurso, AsignacionActividad,
    ActividadMultimedia, ActividadTexto, Pregunta, OpcionRespuesta
)
from .utils.validators import validar_opciones_pregunta, validar_preguntas_actividad

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=False)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'rol', 'nombre_completo']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }
    
    def create(self, validated_data):
        # Hashear la contraseña antes de guardar
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class LoginResponseSerializer(serializers.Serializer):
    """Serializer para la respuesta del endpoint de login."""
    token = serializers.CharField()
    usuario_id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    nombre_completo = serializers.CharField()
    rol = serializers.CharField()

class ActividadSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = Actividad
        fields = ['id', 'titulo', 'descripcion', 'tipo', 'template_type', 'recurso', 'fecha_limite', 'estado', 'curso', 'curso_nombre', 'creado_por', 'fecha_creacion']
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
    """Serializer for EstudianteCurso with nested complete estudiante object."""
    estudiante = UsuarioSerializer(read_only=True)
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    
    class Meta:
        model = EstudianteCurso
        fields = ['id', 'estudiante', 'curso', 'curso_nombre', 'fecha_inscripcion']


class EstudianteCursoWriteSerializer(serializers.ModelSerializer):
    """Write-only serializer for EstudianteCurso POST/PUT operations."""
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


# ========== SERIALIZERS PARA SISTEMA DE PLANTILLAS ==========

class ActividadMultimediaSerializer(serializers.ModelSerializer):
    """
    Serializer para actividades multimedia.
    Maneja la información específica de archivos multimedia alojados en Cloudinary.
    """
    class Meta:
        model = ActividadMultimedia
        fields = [
            'id', 'actividad', 'archivo_url_cloudinary', 'tipo_archivo',
            'duracion_segundos', 'tamaño_bytes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ActividadTextoSerializer(serializers.ModelSerializer):
    """
    Serializer para actividades de texto.
    Maneja la configuración específica de actividades basadas en preguntas.
    """
    class Meta:
        model = ActividadTexto
        fields = [
            'id', 'actividad', 'tiempo_limite_minutos', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class OpcionRespuestaSerializer(serializers.ModelSerializer):
    """
    Serializer para opciones de respuesta de preguntas.
    Incluye validación para asegurar que solo una opción sea correcta.
    """
    class Meta:
        model = OpcionRespuesta
        fields = [
            'texto', 'es_correcta', 'orden'
        ]
        read_only_fields = ['id', 'created_at']


class PreguntaSerializer(serializers.ModelSerializer):
    """
    Serializer para preguntas de actividades.
    Incluye las opciones de respuesta relacionadas.
    """
    opciones = OpcionRespuestaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pregunta
        fields = [
            'id', 'actividad', 'enunciado', 'orden', 'created_at', 'opciones'
        ]
        read_only_fields = ['id', 'created_at']


class PreguntaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear preguntas con sus opciones de respuesta.
    Incluye validación de que haya al menos una opción correcta.
    """
    opciones = OpcionRespuestaSerializer(many=True, write_only=True)
    
    class Meta:
        model = Pregunta
        fields = [
            'enunciado', 'orden', 'opciones'
        ]
        read_only_fields = ['id']
    
    def validate_opciones(self, value):
        """Valida que haya al menos 2 opciones y exactamente 1 correcta."""
        return validar_opciones_pregunta(value)
    
    def create(self, validated_data):
        opciones_data = validated_data.pop('opciones')
        pregunta = Pregunta.objects.create(**validated_data)
        
        # Crear las opciones de respuesta
        for opcion_data in opciones_data:
            OpcionRespuesta.objects.create(pregunta=pregunta, **opcion_data)
        
        return pregunta


class ActividadConPreguntasMixin:
    """
    Mixin reutilizable para serializers de creación de actividades con preguntas.

    Centraliza el método create() que es idéntico en ActividadMultimediaCreateSerializer
    y ActividadTextoCreateSerializer, eliminando duplicación.

    Uso: heredar este mixin ANTES de serializers.ModelSerializer en la MRO.
    """

    # Subclases deben definir estos atributos para inyectar valores fijos.
    TEMPLATE_TYPE: str = ''
    TIPO: str = ''

    def to_internal_value(self, data):
        """
        Inyecta template_type y tipo fijos antes de la validación de campos.

        Esto reemplaza el antipatrón de mutar self.initial_data en __init__,
        que falla cuando el serializer se instancia sin el argumento data=
        (p.ej. en tests o en lecturas).
        """
        data = data.copy()
        if self.TEMPLATE_TYPE:
            data['template_type'] = self.TEMPLATE_TYPE
        if self.TIPO:
            data['tipo'] = self.TIPO
        return super().to_internal_value(data)

    def create(self, validated_data):
        """
        Crea la actividad base y luego crea cada pregunta con sus opciones.
        """
        preguntas_data = validated_data.pop('preguntas')

        actividad = super().create(validated_data)

        for pregunta_data in preguntas_data:
            pregunta_data['actividad'] = actividad
            PreguntaCreateSerializer().create(pregunta_data)

        return actividad


class ActividadMultimediaCreateSerializer(ActividadConPreguntasMixin, serializers.ModelSerializer):
    """
    Serializer para crear actividades multimedia completas.
    Fuerza template_type='multimedia' y tipo='video' sobre los datos entrantes.
    """

    TEMPLATE_TYPE = 'multimedia'
    TIPO = 'video'

    preguntas = PreguntaCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Actividad
        fields = [
            'titulo', 'descripcion', 'tipo', 'template_type', 'curso',
            'fecha_limite', 'preguntas'
        ]

    def validate_preguntas(self, value):
        """Valida que haya al menos una pregunta."""
        return validar_preguntas_actividad(value, tipo_actividad='multimedia')


class ActividadTextoCreateSerializer(ActividadConPreguntasMixin, serializers.ModelSerializer):
    """
    Serializer para crear actividades de texto completas.
    Fuerza template_type='texto' y tipo='quiz_ciencias' sobre los datos entrantes.
    """

    TEMPLATE_TYPE = 'texto'
    TIPO = 'quiz_ciencias'

    preguntas = PreguntaCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Actividad
        fields = [
            'titulo', 'descripcion', 'tipo', 'template_type', 'curso',
            'fecha_limite', 'preguntas'
        ]

    def validate_preguntas(self, value):
        """Valida que haya al menos una pregunta."""
        return validar_preguntas_actividad(value, tipo_actividad='texto')


class ActividadCompletaSerializer(serializers.ModelSerializer):
    """
    Serializer para obtener actividades completas con toda su información.
    Incluye multimedia, preguntas y opciones según el tipo de plantilla.
    """
    curso_nombre = serializers.CharField(source='curso.nombre', read_only=True)
    multimedia = ActividadMultimediaSerializer(read_only=True)
    texto = ActividadTextoSerializer(read_only=True)
    preguntas = PreguntaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Actividad
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'template_type', 'recurso',
            'fecha_limite', 'estado', 'curso', 'curso_nombre', 'creado_por',
            'fecha_creacion', 'multimedia', 'texto', 'preguntas'
        ]
        read_only_fields = ['creado_por', 'fecha_creacion']
