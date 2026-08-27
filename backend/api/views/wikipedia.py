import requests
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from api.permissions import IsProfesor, IsAdministrador

from ..models import Usuario, Curso, Actividad


@api_view(['GET'])
def obtener_contenido_wikipedia(request):
    """Obtener contenido educativo de Wikipedia para ciencias naturales."""
    tema = request.GET.get('tema', '')
    if not tema:
        return Response({'mensaje': 'Debe proporcionar un tema'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        search_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema}"
        response = requests.get(search_url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            contenido_educativo = {
                'titulo': data.get('title', ''),
                'resumen': data.get('extract', ''),
                'imagen': data.get('thumbnail', {}).get('source', ''),
                'url_completa': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'tipo_contenido': 'wikipedia',
                'materia': 'ciencias_naturales'
            }
            return Response(contenido_educativo, status=status.HTTP_200_OK)

        return Response({'mensaje': 'Tema no encontrado en Wikipedia'}, status=status.HTTP_404_NOT_FOUND)
    except requests.RequestException as e:
        return Response({'mensaje': f'Error al conectar con Wikipedia: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def buscar_temas_ciencias(request):
    """Buscar múltiples temas de ciencias naturales en Wikipedia."""
    query = request.GET.get('query', '')
    if not query:
        return Response({'mensaje': 'Debe proporcionar una consulta'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        search_url = "https://es.wikipedia.org/api/rest_v1/page/search"
        params = {
            'q': f"{query} ciencias naturales biología física química",
            'limit': 10
        }
        response = requests.get(search_url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            resultados = []
            for articulo in data.get('pages', []):
                resultados.append({
                    'titulo': articulo.get('title', ''),
                    'descripcion': articulo.get('description', ''),
                    'resumen': articulo.get('extract', ''),
                    'imagen': articulo.get('thumbnail', {}).get('source', '') if articulo.get('thumbnail') else '',
                    'key': articulo.get('key', ''),
                    'materia': 'ciencias_naturales'
                })
            return Response({'resultados': resultados, 'total': len(resultados)}, status=status.HTTP_200_OK)

        return Response({'mensaje': 'Error en la búsqueda'}, status=status.HTTP_404_NOT_FOUND)
    except requests.RequestException as e:
        return Response({'mensaje': f'Error al conectar con Wikipedia: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def generar_actividad_wikipedia(request):
    """Generar una actividad basada en contenido de Wikipedia."""
    usuario = request.user
    tema_wikipedia = request.data.get('tema')
    curso_id = request.data.get('curso')

    if not all([tema_wikipedia, curso_id]):
        return Response({'mensaje': 'Faltan datos requeridos: tema y curso'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        curso = Curso.objects.get(id=curso_id)
        search_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema_wikipedia}"
        response = requests.get(search_url, timeout=10)

        if response.status_code == 200:
            wiki_data = response.json()
            titulo = f"Exploración: {wiki_data.get('title', tema_wikipedia)}"
            descripcion = f"""
            **Actividad de Ciencias Naturales basada en Wikipedia**

            **Tema:** {wiki_data.get('title', '')}

            **Resumen:** {wiki_data.get('extract', '')[:300]}...

            **Instrucciones:**
            1. Lee el contenido proporcionado
            2. Identifica los conceptos clave
            3. Responde las preguntas de comprensión
            4. Investiga más sobre el tema

            **Fuente:** {wiki_data.get('content_urls', {}).get('desktop', {}).get('page', '')}
            """
            actividad = Actividad.objects.create(
                titulo=titulo,
                descripcion=descripcion,
                tipo='lectura_comprensiva',
                curso=curso,
                creado_por=usuario,
            )
            return Response({
                'mensaje': 'Actividad creada exitosamente',
                'actividad_id': actividad.id,
                'titulo': actividad.titulo,
                'contenido_wikipedia': {
                    'titulo': wiki_data.get('title', ''),
                    'resumen': wiki_data.get('extract', ''),
                    'imagen': wiki_data.get('thumbnail', {}).get('source', ''),
                    'url': wiki_data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                }
            }, status=status.HTTP_201_CREATED)

        return Response({'mensaje': 'Tema no encontrado en Wikipedia'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
