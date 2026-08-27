"""
Validadores para archivos multimedia y actividades con plantillas.
"""
from django.core.exceptions import ValidationError
from django.conf import settings
import mimetypes
import os


def validate_multimedia_file(file_obj):
    """
    Valida que un archivo sea un archivo multimedia válido (video, audio o imagen).
    
    Parámetros:
        file_obj: Objeto de archivo a validar
        
    Levanta:
        ValidationError: Si el archivo no es válido
    """
    # Validar tamaño máximo
    max_size = getattr(settings, 'CLOUDINARY_MAX_FILE_SIZE', 104857600)  # 100MB
    if file_obj.size > max_size:
        raise ValidationError(
            f'El archivo es demasiado grande. Tamaño máximo: {max_size / (1024*1024):.0f}MB'
        )
    
    # Validar extensión y tipo MIME
    filename = file_obj.name
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    allowed_formats = (
        getattr(settings, 'CLOUDINARY_ALLOWED_VIDEO_FORMATS', []) +
        getattr(settings, 'CLOUDINARY_ALLOWED_AUDIO_FORMATS', []) +
        getattr(settings, 'CLOUDINARY_ALLOWED_IMAGE_FORMATS', [])
    )
    
    if ext not in allowed_formats:
        raise ValidationError(
            f'Formato de archivo no permitido: {ext}. '
            f'Formatos válidos: {", ".join(allowed_formats)}'
        )
    
    return file_obj


def validate_video_file(file_obj):
    """
    Valida que un archivo sea un video válido.
    
    Parámetros:
        file_obj: Objeto de archivo de video
        
    Levanta:
        ValidationError: Si no es un video válido
    """
    filename = file_obj.name
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    allowed_formats = getattr(settings, 'CLOUDINARY_ALLOWED_VIDEO_FORMATS', [])
    
    if ext not in allowed_formats:
        raise ValidationError(
            f'El archivo debe ser un video. '
            f'Formatos válidos: {", ".join(allowed_formats)}'
        )
    
    # Validar tamaño (videos pueden ser más grandes)
    max_video_size = getattr(settings, 'CLOUDINARY_MAX_FILE_SIZE', 104857600)
    if file_obj.size > max_video_size:
        raise ValidationError(
            f'El video es demasiado grande. Tamaño máximo: {max_video_size / (1024*1024):.0f}MB'
        )
    
    return file_obj


def validate_audio_file(file_obj):
    """
    Valida que un archivo sea un audio válido.
    
    Parámetros:
        file_obj: Objeto de archivo de audio
        
    Levanta:
        ValidationError: Si no es un audio válido
    """
    filename = file_obj.name
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    allowed_formats = getattr(settings, 'CLOUDINARY_ALLOWED_AUDIO_FORMATS', [])
    
    if ext not in allowed_formats:
        raise ValidationError(
            f'El archivo debe ser un audio. '
            f'Formatos válidos: {", ".join(allowed_formats)}'
        )
    
    # Validar tamaño
    max_size = getattr(settings, 'CLOUDINARY_MAX_FILE_SIZE', 104857600)
    if file_obj.size > max_size:
        raise ValidationError(
            f'El audio es demasiado grande. Tamaño máximo: {max_size / (1024*1024):.0f}MB'
        )
    
    return file_obj


def validate_image_file(file_obj):
    """
    Valida que un archivo sea una imagen válida.
    
    Parámetros:
        file_obj: Objeto de archivo de imagen
        
    Levanta:
        ValidationError: Si no es una imagen válida
    """
    filename = file_obj.name
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    allowed_formats = getattr(settings, 'CLOUDINARY_ALLOWED_IMAGE_FORMATS', [])
    
    if ext not in allowed_formats:
        raise ValidationError(
            f'El archivo debe ser una imagen. '
            f'Formatos válidos: {", ".join(allowed_formats)}'
        )
    
    # Validar tamaño (imágenes más pequeñas)
    max_image_size = 52428800  # 50MB
    if file_obj.size > max_image_size:
        raise ValidationError(
            f'La imagen es demasiado grande. Tamaño máximo: 50MB'
        )
    
    return file_obj


def detect_file_type(file_obj):
    """
    Detecta el tipo de archivo multimedia (video, audio, imagen).
    
    Parámetros:
        file_obj: Objeto de archivo
        
    Retorna:
        str: Tipo de archivo ('video', 'audio', 'imagen') o 'unknown'
    """
    filename = file_obj.name
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    
    video_formats = getattr(settings, 'CLOUDINARY_ALLOWED_VIDEO_FORMATS', [])
    audio_formats = getattr(settings, 'CLOUDINARY_ALLOWED_AUDIO_FORMATS', [])
    image_formats = getattr(settings, 'CLOUDINARY_ALLOWED_IMAGE_FORMATS', [])
    
    if ext in video_formats:
        return 'video'
    elif ext in audio_formats:
        return 'audio'
    elif ext in image_formats:
        return 'imagen'
    else:
        return 'unknown'


# ========== VALIDADORES DE NEGOCIO (Serializers / Actividades) ==========

def validar_opciones_pregunta(opciones: list) -> list:
    """
    Valida que una lista de opciones cumpla las reglas de negocio:
      - Al menos 2 opciones de respuesta.
      - Exactamente 1 opción marcada como correcta.

    Parámetros:
        opciones: Lista de dicts con las opciones de respuesta.
                  Cada dict debe contener la clave 'es_correcta' (bool).

    Retorna:
        La misma lista si es válida.

    Levanta:
        rest_framework.serializers.ValidationError si no se cumplen las reglas.
    """
    from rest_framework import serializers as drf_serializers

    if len(opciones) < 2:
        raise drf_serializers.ValidationError(
            "Cada pregunta debe tener al menos 2 opciones de respuesta."
        )

    correctas = sum(1 for opcion in opciones if opcion.get('es_correcta', False))
    if correctas != 1:
        raise drf_serializers.ValidationError(
            "Cada pregunta debe tener exactamente una opción correcta."
        )

    return opciones


def validar_preguntas_actividad(preguntas: list, tipo_actividad: str = 'actividad') -> list:
    """
    Valida que una actividad tenga al menos una pregunta.

    Parámetros:
        preguntas: Lista de preguntas a validar.
        tipo_actividad: Etiqueta descriptiva para el mensaje de error
                        (ej. 'multimedia', 'texto'). Por defecto 'actividad'.

    Retorna:
        La misma lista si es válida.

    Levanta:
        rest_framework.serializers.ValidationError si la lista está vacía.
    """
    from rest_framework import serializers as drf_serializers

    if not preguntas:
        raise drf_serializers.ValidationError(
            f"La actividad de {tipo_actividad} debe tener al menos una pregunta."
        )

    return preguntas
