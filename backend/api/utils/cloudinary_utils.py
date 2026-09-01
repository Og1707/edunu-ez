"""
Utilidades para manejo de archivos multimedia con Cloudinary.

Proporciona funciones para:
- Subir archivos a Cloudinary
- Obtener información de archivos
- Generar URLs firmadas
- Manipular archivos existentes
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
import cloudinary.utils
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError
from .validators import detect_file_type, validate_multimedia_file
import logging

logger = logging.getLogger(__name__)


def upload_multimedia_file(file_obj, public_id_prefix='actividades', tags=None, folder='multimedia'):
    """
    Sube un archivo multimedia a Cloudinary.
    
    Parámetros:
        file_obj: Archivo a subir
        public_id_prefix: Prefijo para el public_id (default: 'actividades')
        tags: Lista de tags para el archivo (default: None)
        folder: Carpeta en Cloudinary (default: 'multimedia')
        
    Retorna:
        dict: Respuesta de Cloudinary con información del archivo
        {
            'url': URL pública del archivo,
            'secure_url': URL HTTPS del archivo,
            'public_id': ID público del archivo,
            'resource_type': Tipo de recurso (video, image, etc),
            'type': Tipo de entrega (upload, private, etc),
            'duration': Duración en segundos (solo para video/audio),
            'bytes': Tamaño en bytes,
            'width': Ancho (solo para imágenes),
            'height': Alto (solo para imágenes),
            'format': Formato del archivo,
        }
        
    Levanta:
        ValidationError: Si hay error en la validación o upload
    """
    try:
        # Validar archivo
        validate_multimedia_file(file_obj)
        
        # Detectar tipo de archivo
        file_type = detect_file_type(file_obj)
        
        if file_type == 'unknown':
            raise DRFValidationError('Tipo de archivo no reconocido')
        
        # Preparar opciones de upload
        upload_options = {
            'folder': folder,
            'resource_type': 'auto',  # Detecta automáticamente: image, video, raw
            'use_filename': True,
            'unique_filename': True,
            'overwrite': False,
        }
        
        # Agregar tags si se proporcionan
        if tags:
            upload_options['tags'] = tags
        
        # Para videos: incluir información de duración
        if file_type == 'video':
            upload_options['eager'] = [
                {'streaming_profile': 'hd', 'format': 'mp4'}
            ]
            upload_options['eager_async'] = True
        
        # Subir archivo
        logger.info(f"Subiendo archivo: {file_obj.name} a Cloudinary")
        response = cloudinary.uploader.upload(
            file_obj,
            **upload_options
        )
        
        logger.info(f"Archivo subido exitosamente: {response.get('public_id')}")
        
        return {
            'url': response.get('url'),
            'secure_url': response.get('secure_url'),
            'public_id': response.get('public_id'),
            'resource_type': response.get('resource_type'),
            'type': response.get('type'),
            'duration': response.get('duration'),
            'bytes': response.get('bytes'),
            'width': response.get('width'),
            'height': response.get('height'),
            'format': response.get('format'),
            'file_type': file_type,
        }
    
    except ValidationError as e:
        logger.error(f"Error de validación: {str(e)}")
        raise DRFValidationError(str(e))
    except Exception as e:
        logger.error(f"Error al subir archivo a Cloudinary: {str(e)}")
        raise DRFValidationError(f"Error al subir archivo: {str(e)}")


def delete_cloudinary_file(public_id, resource_type='auto'):
    """
    Elimina un archivo de Cloudinary.
    
    Parámetros:
        public_id: ID público del archivo en Cloudinary
        resource_type: Tipo de recurso ('image', 'video', 'raw', 'auto')
        
    Retorna:
        dict: Respuesta de Cloudinary
        
    Levanta:
        ValidationError: Si hay error al eliminar
    """
    try:
        logger.info(f"Eliminando archivo de Cloudinary: {public_id}")
        response = cloudinary.uploader.destroy(
            public_id,
            resource_type=resource_type
        )
        logger.info(f"Archivo eliminado: {public_id}")
        return response
    
    except Exception as e:
        logger.error(f"Error al eliminar archivo de Cloudinary: {str(e)}")
        raise DRFValidationError(f"Error al eliminar archivo: {str(e)}")


def get_file_info(public_id, resource_type='auto'):
    """
    Obtiene información de un archivo en Cloudinary.
    
    Parámetros:
        public_id: ID público del archivo
        resource_type: Tipo de recurso
        
    Retorna:
        dict: Información del archivo
        
    Levanta:
        ValidationError: Si el archivo no existe
    """
    try:
        response = cloudinary.api.resource(
            public_id,
            resource_type=resource_type
        )
        return response
    
    except Exception as e:
        logger.error(f"Error al obtener información del archivo: {str(e)}")
        raise DRFValidationError(f"No se pudo obtener información del archivo: {str(e)}")


def generate_signed_url(public_id, resource_type='image', transformations=None, expiration=3600):
    """
    Genera una URL firmada para un archivo en Cloudinary.
    
    Parámetros:
        public_id: ID público del archivo
        resource_type: Tipo de recurso ('image', 'video', 'raw')
        transformations: Diccionario de transformaciones (url_suffix, width, height, etc)
        expiration: Tiempo de expiración en segundos (default: 1 hora)
        
    Retorna:
        str: URL firmada y segura
    """
    try:
        if transformations is None:
            transformations = {}
        
        transformations['sign_url'] = True
        transformations['secure'] = True
        transformations['type'] = 'authenticated'
        
        url = cloudinary.CloudinaryResource(public_id).build_url(**transformations)
        return url
    
    except Exception as e:
        logger.error(f"Error al generar URL firmada: {str(e)}")
        raise DRFValidationError(f"Error al generar URL: {str(e)}")


def get_upload_signature():
    """
    Genera una firma para uploads no firmados desde el cliente.
    
    Retorna:
        dict: Diccionario con los parámetros necesarios para unsigned upload
        {
            'signature': Firma criptográfica,
            'timestamp': Timestamp de la firma,
            'api_key': API Key de Cloudinary,
            'cloud_name': Nombre de la nube,
        }
    """
    import time
    
    timestamp = int(time.time())
    api_secret = settings.CLOUDINARY_API_SECRET if hasattr(settings, 'CLOUDINARY_API_SECRET') else ''
    api_key = cloudinary.config().api_key
    
    # Generar firma con helper oficial de Cloudinary
    signature = cloudinary.utils.api_sign_request({'timestamp': timestamp}, api_secret)
    
    return {
        'signature': signature,
        'timestamp': timestamp,
        'api_key': api_key,
        'cloud_name': cloudinary.config().cloud_name,
    }


def batch_delete_files(public_ids, resource_type='auto'):
    """
    Elimina múltiples archivos de Cloudinary de forma eficiente.
    
    Parámetros:
        public_ids: Lista de IDs públicos a eliminar
        resource_type: Tipo de recurso
        
    Retorna:
        dict: Información de archivos eliminados y errores
        {
            'deleted': [Lista de públicos IDs eliminados],
            'errors': [{público_id, mensaje_error}],
        }
    """
    deleted = []
    errors = []
    
    for public_id in public_ids:
        try:
            response = delete_cloudinary_file(public_id, resource_type)
            if response.get('result') == 'ok':
                deleted.append(public_id)
        except Exception as e:
            errors.append({
                'public_id': public_id,
                'error': str(e)
            })
            logger.warning(f"No se pudo eliminar {public_id}: {str(e)}")
    
    return {
        'deleted': deleted,
        'errors': errors,
    }
