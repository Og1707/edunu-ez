import json
import requests
from functools import wraps
from django.utils import timezone
from django.db import models
from .models import *
from .serializers import *
from .webhooks import enviar_resultado_actividad_a_n8n, registrar_evento_actividad
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response


class recipientwebhooks (APIView):
    authentication_classes = [] 
    permission_classes = [] ##Para que cualquier webhook pueda acceder

    def post(self, request, *args, **kwargs):
        try: 
            payload: request.data ##Intentara parseal el JSON
        except Exception:
            payload = json.loads(request.body.decode('utf-8'))
        print ('webhook recibido',payload)
        # Aquí puedes procesar el payload como desees
        return Response({'mensaje': 'Webhook recibido'}, status=status.HTTP_200_OK)


@api_view(['GET','POST'])
def registrar_usuario(request):
    """
    Endpoint para registrar un nuevo usuario.
    Espera un JSON con los campos necesarios para crear un Usuario.
    """
    serializer = UsuarioSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class usuarioviewset(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD de Usuario.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

@api_view(['GET', 'POST'])
def login_usuario(request):
    """
    Endpoint para iniciar sesión de un usuario.
    Espera un JSON con 'email' y 'password'.
    """
    from django.contrib.auth import authenticate
    
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'mensaje': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Buscar usuario por email
        usuario = Usuario.objects.get(email=email)
        
        # Verificar contraseña usando el sistema de autenticación de Django
        if usuario.check_password(password):
            return Response({
                'mensaje': 'Inicio de sesión exitoso',
                'usuario_id': usuario.id,
                'email': usuario.email,
                'username': usuario.username,
                'nombre_completo': usuario.nombre_completo,
                'rol': usuario.rol
            }, status=status.HTTP_200_OK)
        else:
            return Response({'mensaje': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)
            
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET', 'POST'])
def gestionar_actividades(request):
    """
    Endpoint para listar y crear actividades.
    GET: Lista actividades según permisos del usuario
    POST: Crea una nueva actividad (solo profesores y administradores)
    """
    if request.method == 'GET':
        user_id = request.GET.get('user_id')

        if user_id:
            # Si se proporciona user_id, filtrar según permisos
            try:
                usuario = Usuario.objects.get(id=user_id)

                if usuario.rol == 'estudiante':
                    # Para estudiantes, usar la función específica
                    return obtener_actividades_estudiante(request)
                elif usuario.rol == 'profesor':
                    # Para profesores, usar la función específica
                    return obtener_actividades_profesor(request)
                elif usuario.rol == 'administrador':
                    # Para administradores, mostrar todas las actividades
                    actividades = Actividad.objects.all().order_by('-fecha_creacion')
                    serializer = ActividadSerializer(actividades, many=True)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response({'mensaje': 'Rol no reconocido'}, status=status.HTTP_403_FORBIDDEN)

            except Usuario.DoesNotExist:
                return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Si no se proporciona user_id, mostrar todas las actividades (para compatibilidad)
            actividades = Actividad.objects.all().order_by('-fecha_creacion')
            serializer = ActividadSerializer(actividades, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        # Verificar que el usuario esté autenticado (simulado con user_id por ahora)
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            usuario = Usuario.objects.get(id=user_id)
            if usuario.rol not in ['profesor', 'administrador']:
                return Response({'mensaje': 'No tienes permisos para crear actividades'}, status=status.HTTP_403_FORBIDDEN)
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Crear la actividad
        serializer = ActividadSerializer(data=request.data)
        if serializer.is_valid():
            # Asignar el usuario que crea la actividad
            serializer.save(creado_por=usuario)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def obtener_tipos_actividad(request):
    """
    Endpoint para obtener los tipos de actividad disponibles.
    """
    tipos = [{'value': tipo[0], 'label': tipo[1]} for tipo in Actividad.TIPOS]
    return Response(tipos, status=status.HTTP_200_OK)

@api_view(['GET'])
def listar_cursos(request):
    """
    Endpoint para listar todos los cursos disponibles.
    """
    cursos = Curso.objects.all().order_by('nombre')
    serializer = CursoSerializer(cursos, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def obtener_actividades_profesor(request):
    """
    Obtener actividades que un profesor puede gestionar (actividades de sus cursos)
    """
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        profesor = Usuario.objects.get(id=user_id, rol='profesor')

        # Obtener cursos del profesor
        cursos_profesor = Curso.objects.filter(profesor=profesor)

        if not cursos_profesor.exists():
            return Response({'mensaje': 'No tienes cursos asignados'}, status=status.HTTP_404_NOT_FOUND)

        # Obtener actividades de los cursos del profesor
        actividades = Actividad.objects.filter(curso__in=cursos_profesor).order_by('-fecha_creacion')

        actividades_data = []
        for actividad in actividades:
            # Obtener estadísticas de asignación
            asignaciones = AsignacionActividad.objects.filter(actividad=actividad)
            estudiantes_curso = EstudianteCurso.objects.filter(curso=actividad.curso).count()

            actividad_data = ActividadSerializer(actividad).data
            actividad_data['estadisticas'] = {
                'total_estudiantes': estudiantes_curso,
                'total_asignaciones': asignaciones.count(),
                'completadas': asignaciones.filter(estado__in=['completada', 'revisada', 'calificada']).count(),
                'pendientes': asignaciones.filter(estado='asignada').count(),
                'en_progreso': asignaciones.filter(estado='en_progreso').count(),
                'porcentaje_asignado': round((asignaciones.count() / estudiantes_curso * 100) if estudiantes_curso > 0 else 0, 1)
            }

            actividades_data.append(actividad_data)

        return Response(actividades_data, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def crear_curso(request):
    """
    Endpoint para crear un nuevo curso.
    Solo profesores y administradores pueden crear cursos.
    """
    user_id = request.data.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        usuario = Usuario.objects.get(id=user_id)
        if usuario.rol not in ['profesor', 'administrador']:
            return Response({'mensaje': 'No tienes permisos para crear cursos'}, status=status.HTTP_403_FORBIDDEN)
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    datos_curso = request.data.copy()
    # Si es administrador y se proporciona un profesor, usar ese profesor
    if usuario.rol == 'administrador' and datos_curso.get('profesor'):
        try:
            profesor = Usuario.objects.get(id=datos_curso['profesor'], rol='profesor')
            datos_curso['profesor'] = profesor.id
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    # Si es profesor, asignar el curso al profesor que lo crea
    elif usuario.rol == 'profesor':
        datos_curso['profesor'] = usuario.id

    serializer = CursoSerializer(data=datos_curso)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def obtener_contenido_wikipedia(request):
    """
    Endpoint para obtener contenido educativo de Wikipedia para ciencias naturales.
    Parámetros: tema (query parameter)
    """
    tema = request.GET.get('tema', '')
    if not tema:
        return Response({'mensaje': 'Debe proporcionar un tema'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Buscar artículos relacionados con el tema
        search_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema}"
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filtrar y estructurar la información para uso educativo
            contenido_educativo = {
                'titulo': data.get('title', ''),
                'resumen': data.get('extract', ''),
                'imagen': data.get('thumbnail', {}).get('source', ''),
                'url_completa': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'tipo_contenido': 'wikipedia',
                'materia': 'ciencias_naturales'
            }
            
            return Response(contenido_educativo, status=status.HTTP_200_OK)
        else:
            return Response({'mensaje': 'Tema no encontrado en Wikipedia'}, status=status.HTTP_404_NOT_FOUND)
            
    except requests.RequestException as e:
        return Response({'mensaje': f'Error al conectar con Wikipedia: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def buscar_temas_ciencias(request):
    """
    Endpoint para buscar múltiples temas de ciencias naturales en Wikipedia.
    """
    query = request.GET.get('query', '')
    if not query:
        return Response({'mensaje': 'Debe proporcionar una consulta'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Buscar artículos relacionados
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
                resultado = {
                    'titulo': articulo.get('title', ''),
                    'descripcion': articulo.get('description', ''),
                    'resumen': articulo.get('extract', ''),
                    'imagen': articulo.get('thumbnail', {}).get('source', '') if articulo.get('thumbnail') else '',
                    'key': articulo.get('key', ''),
                    'materia': 'ciencias_naturales'
                }
                resultados.append(resultado)
            
            return Response({
                'resultados': resultados,
                'total': len(resultados)
            }, status=status.HTTP_200_OK)
        else:
            return Response({'mensaje': 'Error en la búsqueda'}, status=status.HTTP_404_NOT_FOUND)
            
    except requests.RequestException as e:
        return Response({'mensaje': f'Error al conectar con Wikipedia: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def generar_actividad_wikipedia(request):
    """
    Endpoint para generar una actividad educativa basada en contenido de Wikipedia.
    """
    user_id = request.data.get('user_id')
    tema_wikipedia = request.data.get('tema')
    curso_id = request.data.get('curso')
    tipo_actividad = request.data.get('tipo', 'lectura_comprensiva')
    
    if not all([user_id, tema_wikipedia, curso_id]):
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verificar usuario y permisos
        usuario = Usuario.objects.get(id=user_id)
        if usuario.rol not in ['profesor', 'administrador']:
            return Response({'mensaje': 'No tienes permisos para crear actividades'}, status=status.HTTP_403_FORBIDDEN)
        
        curso = Curso.objects.get(id=curso_id)
        
        # Obtener contenido de Wikipedia
        search_url = f"https://es.wikipedia.org/api/rest_v1/page/summary/{tema_wikipedia}"
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            wiki_data = response.json()
            
            # Crear actividad basada en el contenido
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
                creado_por=usuario
            )
            
            return Response({
                'mensaje': 'Actividad creada exitosamente',
                'actividad_id': actividad.id,
                'titulo': actividad.titulo,
                'contenido_wikipedia': {
                    'titulo': wiki_data.get('title', ''),
                    'resumen': wiki_data.get('extract', ''),
                    'imagen': wiki_data.get('thumbnail', {}).get('source', ''),
                    'url': wiki_data.get('content_urls', {}).get('desktop', {}).get('page', '')
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'mensaje': 'Tema no encontrado en Wikipedia'}, status=status.HTTP_404_NOT_FOUND)
            
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
def gestionar_materias_ciencias(request):
    """
    Endpoint para listar y crear materias de ciencias naturales.
    GET: Lista todas las materias de ciencias
    POST: Crea una nueva materia (solo administradores)
    """
    if request.method == 'GET':
        area = request.GET.get('area', '')
        nivel = request.GET.get('nivel', '')
        
        materias = MateriaCienciasNaturales.objects.filter(activa=True)
        
        if area:
            materias = materias.filter(area=area)
        if nivel:
            materias = materias.filter(nivel_educativo=nivel)
            
        materias = materias.order_by('area', 'nivel_educativo', 'nombre')
        
        # Serializar manualmente para incluir información adicional
        materias_data = []
        for materia in materias:
            materia_data = {
                'id': materia.id,
                'nombre': materia.nombre,
                'area': materia.area,
                'area_display': materia.get_area_display(),
                'nivel_educativo': materia.nivel_educativo,
                'nivel_display': materia.get_nivel_educativo_display(),
                'descripcion': materia.descripcion,
                'temas_principales': materia.temas_principales,
                'objetivos_aprendizaje': materia.objetivos_aprendizaje,
                'recursos_recomendados': materia.recursos_recomendados,
                'fecha_creacion': materia.fecha_creacion,
                'total_cursos': materia.cursos.count()
            }
            materias_data.append(materia_data)
        
        return Response(materias_data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            usuario = Usuario.objects.get(id=user_id)
            if usuario.rol != 'administrador':
                return Response({'mensaje': 'Solo los administradores pueden crear materias'}, status=status.HTTP_403_FORBIDDEN)
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        # Crear la materia
        try:
            materia = MateriaCienciasNaturales.objects.create(
                nombre=request.data.get('nombre'),
                area=request.data.get('area'),
                nivel_educativo=request.data.get('nivel_educativo'),
                descripcion=request.data.get('descripcion', ''),
                temas_principales=request.data.get('temas_principales', []),
                objetivos_aprendizaje=request.data.get('objetivos_aprendizaje', ''),
                recursos_recomendados=request.data.get('recursos_recomendados', [])
            )
            
            return Response({
                'mensaje': 'Materia creada exitosamente',
                'materia_id': materia.id,
                'nombre': materia.nombre,
                'area': materia.get_area_display(),
                'nivel': materia.get_nivel_educativo_display()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'mensaje': f'Error al crear la materia: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def obtener_areas_ciencias(request):
    """
    Endpoint para obtener las áreas de ciencias naturales disponibles.
    """
    areas = [{'value': area[0], 'label': area[1]} for area in MateriaCienciasNaturales.AREAS_CIENCIAS]
    return Response(areas, status=status.HTTP_200_OK)

@api_view(['GET'])
def obtener_niveles_educativos(request):
    """
    Endpoint para obtener los niveles educativos disponibles.
    """
    niveles = [{'value': nivel[0], 'label': nivel[1]} for nivel in MateriaCienciasNaturales.NIVELES_EDUCATIVOS]
    return Response(niveles, status=status.HTTP_200_OK)

@api_view(['POST'])
def crear_curso_ciencias(request):
    """
    Endpoint para crear un curso específico de ciencias naturales.
    """
    user_id = request.data.get('user_id')
    materia_id = request.data.get('materia_id')
    nombre_curso = request.data.get('nombre_curso')
    descripcion_curso = request.data.get('descripcion_curso', '')
    unidades_tematicas = request.data.get('unidades_tematicas', [])
    metodologia = request.data.get('metodologia', '')
    
    if not all([user_id, materia_id, nombre_curso]):
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        usuario = Usuario.objects.get(id=user_id)
        if usuario.rol not in ['profesor', 'administrador']:
            return Response({'mensaje': 'No tienes permisos para crear cursos'}, status=status.HTTP_403_FORBIDDEN)
        
        materia = MateriaCienciasNaturales.objects.get(id=materia_id)
        
        # Crear el curso base
        curso = Curso.objects.create(
            nombre=nombre_curso,
            descripcion=descripcion_curso,
            profesor=usuario if usuario.rol == 'profesor' else None
        )
        
        # Crear la extensión de ciencias naturales
        curso_ciencias = CursoCienciasNaturales.objects.create(
            curso=curso,
            materia=materia,
            unidades_tematicas=unidades_tematicas,
            metodologia=metodologia,
            evaluacion_criterios={
                'participacion': 20,
                'tareas': 30,
                'examenes': 50
            }
        )
        
        return Response({
            'mensaje': 'Curso de ciencias naturales creado exitosamente',
            'curso_id': curso.id,
            'nombre': curso.nombre,
            'materia': materia.nombre,
            'area': materia.get_area_display(),
            'nivel': materia.get_nivel_educativo_display()
        }, status=status.HTTP_201_CREATED)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except MateriaCienciasNaturales.DoesNotExist:
        return Response({'mensaje': 'Materia no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def obtener_temas_sugeridos(request):
    """
    Endpoint para obtener temas sugeridos basados en el área de ciencias.
    """
    area = request.GET.get('area', '')
    
    temas_por_area = {
        'biologia': [
            'Célula y sus componentes',
            'Sistemas del cuerpo humano',
            'Genética básica',
            'Ecosistemas y biodiversidad',
            'Evolución',
            'Fotosíntesis y respiración',
            'Clasificación de seres vivos'
        ],
        'fisica': [
            'Mecánica y movimiento',
            'Fuerzas y energía',
            'Ondas y sonido',
            'Luz y óptica',
            'Electricidad y magnetismo',
            'Calor y temperatura',
            'Astronomía básica'
        ],
        'quimica': [
            'Estructura atómica',
            'Tabla periódica',
            'Enlaces químicos',
            'Reacciones químicas',
            'Estados de la materia',
            'Ácidos y bases',
            'Química orgánica básica'
        ],
        'ciencias_tierra': [
            'Geología y minerales',
            'Placas tectónicas',
            'Ciclo del agua',
            'Clima y meteorología',
            'Recursos naturales',
            'Contaminación ambiental'
        ],
        'astronomia': [
            'Sistema solar',
            'Estrellas y galaxias',
            'Exploración espacial',
            'Fases lunares',
            'Constelaciones'
        ],
        'ecologia': [
            'Cadenas alimentarias',
            'Ciclos biogeoquímicos',
            'Conservación ambiental',
            'Cambio climático',
            'Desarrollo sostenible'
        ]
    }
    
    temas = temas_por_area.get(area, [])
    return Response({'area': area, 'temas_sugeridos': temas}, status=status.HTTP_200_OK)

# ========== ENDPOINTS PARA ASIGNACIÓN DE ACTIVIDADES ==========

@api_view(['POST'])
def asignar_actividad_curso(request):
    """
    Endpoint flexible para asignar una o varias actividades a todo un curso.
    """
    user_id = request.data.get('user_id')
    curso_id = request.data.get('curso_id')
    # Permitir ambos esquemas: actividad_id único o lista de actividad_ids
    actividad_id = request.data.get('actividad_id')
    actividad_ids = request.data.get('actividad_ids', [])
    # Si actividad_id viene, agregarlo a la lista
    if actividad_id:
        actividad_ids = [actividad_id]
    # Filtrar falsos positivos (None, '', etc)
    actividad_ids = [aid for aid in actividad_ids if aid]

    if not all([user_id, curso_id]) or not actividad_ids:
        return Response({'mensaje': 'Faltan datos requeridos: user_id, curso_id y al menos una actividad'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Verificar que el usuario sea profesor
        profesor = Usuario.objects.get(id=user_id)
        if profesor.rol != 'profesor':
            return Response({'mensaje': 'Solo los profesores pueden asignar actividades'}, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que el curso existe
        curso = Curso.objects.get(id=curso_id)
        
        # Verificar que el profesor puede asignar actividades en este curso
        if curso.profesor != profesor and profesor.rol != 'administrador':
            print(f"DEBUG: Error de permisos - profesor {profesor.username} no es dueño del curso {curso.nombre}")
            return Response({'mensaje': 'Solo puedes asignar actividades en cursos que diriges'}, status=status.HTTP_403_FORBIDDEN)
        
        # Obtener todos los estudiantes del curso
        estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).select_related('estudiante')
        
        if not estudiantes_curso.exists():
            print(f"DEBUG: No hay estudiantes en el curso {curso.nombre}")
            return Response({'mensaje': 'No hay estudiantes inscritos en este curso'}, status=status.HTTP_400_BAD_REQUEST)
        
        asignaciones_creadas = []
        asignaciones_existentes = []
        errores = []
        actividades_procesadas = []
        
        # Verificar que todas las actividades existen y pertenecen al curso
        for actividad_id in actividad_ids:
            try:
                actividad = Actividad.objects.get(id=actividad_id, curso=curso)
                actividades_procesadas.append(actividad)
            except Actividad.DoesNotExist:
                errores.append(f"Actividad {actividad_id} no encontrada o no pertenece al curso {curso.nombre}")
                continue
        
        if not actividades_procesadas:
            print(f"DEBUG: No se encontraron actividades válidas para asignar")
            return Response({
                'mensaje': 'No se encontraron actividades válidas para asignar',
                'errores': errores
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Procesar las asignaciones
        for actividad in actividades_procesadas:
            for estudiante_curso in estudiantes_curso:
                try:
                    estudiante = estudiante_curso.estudiante
                    
                    # Crear o verificar la asignación
                    asignacion, created = AsignacionActividad.objects.get_or_create(
                        actividad=actividad,
                        estudiante=estudiante,
                        defaults={
                            'profesor': profesor,
                            'estado': 'asignada'
                        }
                    )
                    
                    if created:
                        asignaciones_creadas.append({
                            'estudiante_id': estudiante.id,
                            'estudiante': estudiante.username,
                            'estudiante_nombre': estudiante.nombre_completo,
                            'email': estudiante.email
                        })
                    else:
                        asignaciones_existentes.append({
                            'estudiante_id': estudiante.id,
                            'estudiante': estudiante.username,
                            'estudiante_nombre': estudiante.nombre_completo,
                            'estado_actual': asignacion.estado
                        })
                        
                except Exception as e:
                    errores.append(f"Error al procesar estudiante: {str(e)}")
        
        return Response({
            'mensaje': 'Actividad asignada al curso exitosamente',
            'curso': curso.nombre,
            'actividad': actividad.titulo,
            'nuevas_asignaciones': asignaciones_creadas,
            'asignaciones_existentes': asignaciones_existentes,
            'resumen': {
                'total_estudiantes': len(estudiantes_curso),
                'nuevas_asignaciones': len(asignaciones_creadas),
                'ya_asignadas': len(asignaciones_existentes),
                'errores': len(errores)
            },
            'errores': errores
        }, status=status.HTTP_201_CREATED)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def listar_estudiantes_curso(request):
    """
    Endpoint para listar estudiantes de un curso específico.
    """
    curso_id = request.GET.get('curso_id')
    user_id = request.GET.get('user_id')
    
    if not all([curso_id, user_id]):
        return Response({'mensaje': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verificar que el usuario sea profesor
        profesor = Usuario.objects.get(id=user_id)
        if profesor.rol != 'profesor':
            return Response({'mensaje': 'Solo los profesores pueden ver estudiantes'}, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que el curso existe
        curso = Curso.objects.get(id=curso_id)
        
        # Obtener estudiantes del curso
        estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).select_related('estudiante')
        
        estudiantes_data = []
        for ec in estudiantes_curso:
            estudiante = ec.estudiante
            estudiantes_data.append({
                'id': estudiante.id,
                'username': estudiante.username,
                'nombre_completo': estudiante.nombre_completo,
                'email': estudiante.email,
                'fecha_inscripcion': ec.fecha_inscripcion
            })
        
        return Response({
            'curso': curso.nombre,
            'estudiantes': estudiantes_data,
            'total_estudiantes': len(estudiantes_data)
        }, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def actividades_asignadas_estudiante(request):
    """
    Endpoint para que un estudiante vea sus actividades asignadas.
    """
    user_id = request.GET.get('user_id')
    
    if not user_id:
        return Response({'mensaje': 'ID de usuario requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verificar que el usuario sea estudiante
        estudiante = Usuario.objects.get(id=user_id)
        if estudiante.rol != 'estudiante':
            return Response({'mensaje': 'Solo los estudiantes pueden ver sus actividades asignadas'}, status=status.HTTP_403_FORBIDDEN)
        
        # Obtener actividades asignadas
        asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related(
            'actividad', 'actividad__curso', 'profesor'
        ).order_by('-fecha_asignacion')
        
        actividades_data = []
        for asignacion in asignaciones:
            actividad = asignacion.actividad
            actividades_data.append({
                'asignacion_id': asignacion.id,
                'actividad_id': actividad.id,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'tipo': actividad.tipo,
                'tipo_display': dict(actividad.TIPOS).get(actividad.tipo),
                'curso': actividad.curso.nombre,
                'profesor': asignacion.profesor.nombre_completo,
                'fecha_asignacion': asignacion.fecha_asignacion,
                'fecha_limite': actividad.fecha_limite,
                'estado': asignacion.estado,
                'estado_display': dict(asignacion.ESTADOS_ASIGNACION).get(asignacion.estado),
                'calificacion': asignacion.calificacion,
                'comentarios_profesor': asignacion.comentarios_profesor,
                'tiene_entrega': bool(asignacion.archivo_entrega)
            })
        
        return Response({
            'actividades_asignadas': actividades_data,
            'total_actividades': len(actividades_data)
        }, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def actividades_curso_profesor(request):
    """
    Endpoint para que un profesor vea todas las actividades de sus cursos y su estado de asignación.
    """
    user_id = request.GET.get('user_id')
    curso_id = request.GET.get('curso_id')
    
    if not user_id:
        return Response({'mensaje': 'ID de usuario requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verificar que el usuario sea profesor
        profesor = Usuario.objects.get(id=user_id)
        if profesor.rol != 'profesor':
            return Response({'mensaje': 'Solo los profesores pueden ver actividades de cursos'}, status=status.HTTP_403_FORBIDDEN)
        
        # Si se especifica un curso, filtrar por ese curso
        if curso_id:
            cursos = Curso.objects.filter(id=curso_id, profesor=profesor)
        else:
            cursos = Curso.objects.filter(profesor=profesor)
        
        cursos_data = []
        for curso in cursos:
            # Obtener actividades del curso
            actividades = Actividad.objects.filter(curso=curso).order_by('-fecha_creacion')
            
            actividades_data = []
            for actividad in actividades:
                # Contar asignaciones
                total_asignaciones = AsignacionActividad.objects.filter(actividad=actividad).count()
                total_estudiantes_curso = EstudianteCurso.objects.filter(curso=curso).count()
                
                actividades_data.append({
                    'id': actividad.id,
                    'titulo': actividad.titulo,
                    'descripcion': actividad.descripcion,
                    'tipo': actividad.tipo,
                    'tipo_display': dict(actividad.TIPOS).get(actividad.tipo),
                    'fecha_creacion': actividad.fecha_creacion,
                    'fecha_limite': actividad.fecha_limite,
                    'estado': actividad.estado,
                    'asignaciones': {
                        'total_asignadas': total_asignaciones,
                        'total_estudiantes': total_estudiantes_curso,
                        'porcentaje_asignado': round((total_asignaciones / total_estudiantes_curso * 100) if total_estudiantes_curso > 0 else 0, 1),
                        'esta_asignada_completa': total_asignaciones == total_estudiantes_curso
                    }
                })
            
            cursos_data.append({
                'curso_id': curso.id,
                'curso_nombre': curso.nombre,
                'total_estudiantes': EstudianteCurso.objects.filter(curso=curso).count(),
                'actividades': actividades_data,
                'total_actividades': len(actividades_data)
            })
        
        return Response({
            'profesor': profesor.nombre_completo,
            'cursos': cursos_data,
            'total_cursos': len(cursos_data)
        }, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ========== API DE JUEGOS EDUCATIVOS PARA NIÑOS ==========

@api_view(['GET'])
def listar_categorias_juegos(request):
    """Listar todas las categorías de juegos disponibles"""
    try:
        categorias = CategoriaJuego.objects.filter(activa=True).order_by('nombre')
        
        categorias_data = []
        for categoria in categorias:
            categorias_data.append({
                'id': categoria.id,
                'nombre': categoria.nombre,
                'tipo': categoria.tipo,
                'descripcion': categoria.descripcion,
                'edad_minima': categoria.edad_minima,
                'edad_maxima': categoria.edad_maxima,
                'icono': categoria.icono,
                'total_juegos': categoria.juegos.filter(activo=True).count()
            })
        
        return Response({
            'categorias': categorias_data,
            'total_categorias': len(categorias_data)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def listar_juegos_educativos(request):
    """Listar juegos educativos con filtros opcionales"""
    categoria_id = request.GET.get('categoria_id')
    nivel_dificultad = request.GET.get('nivel_dificultad')
    edad = request.GET.get('edad')
    
    try:
        juegos = JuegoEducativo.objects.filter(activo=True)
        
        # Aplicar filtros
        if categoria_id:
            juegos = juegos.filter(categoria_id=categoria_id)
        
        if nivel_dificultad:
            juegos = juegos.filter(nivel_dificultad=nivel_dificultad)
        
        if edad:
            edad_int = int(edad)
            juegos = juegos.filter(edad_minima__lte=edad_int, edad_maxima__gte=edad_int)
        
        juegos = juegos.select_related('categoria').order_by('categoria__nombre', 'nivel_dificultad')
        
        juegos_data = []
        for juego in juegos:
            juegos_data.append({
                'id': juego.id,
                'titulo': juego.titulo,
                'descripcion': juego.descripcion,
                'categoria': {
                    'id': juego.categoria.id,
                    'nombre': juego.categoria.nombre,
                    'icono': juego.categoria.icono
                },
                'tipo_juego': juego.tipo_juego,
                'tipo_juego_display': dict(juego.TIPOS_JUEGO).get(juego.tipo_juego),
                'nivel_dificultad': juego.nivel_dificultad,
                'nivel_dificultad_display': dict(juego.NIVELES_DIFICULTAD).get(juego.nivel_dificultad),
                'edad_minima': juego.edad_minima,
                'edad_maxima': juego.edad_maxima,
                'tiempo_estimado': juego.tiempo_estimado,
                'objetivos_aprendizaje': juego.objetivos_aprendizaje,
                'habilidades_desarrolla': juego.habilidades_desarrolla,
                'veces_jugado': juego.veces_jugado,
                'puntuacion_promedio': float(juego.puntuacion_promedio),
                'configuracion': juego.configuracion
            })
        
        return Response({
            'juegos': juegos_data,
            'total_juegos': len(juegos_data),
            'filtros_aplicados': {
                'categoria_id': categoria_id,
                'nivel_dificultad': nivel_dificultad,
                'edad': edad
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def crear_juego_educativo(request):
    """Crear un nuevo juego educativo (solo profesores)"""
    user_id = request.data.get('user_id')
    
    if not user_id:
        return Response({'mensaje': 'ID de usuario requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verificar que el usuario sea profesor
        profesor = Usuario.objects.get(id=user_id)
        if profesor.rol != 'profesor':
            return Response({'mensaje': 'Solo los profesores pueden crear juegos'}, status=status.HTTP_403_FORBIDDEN)
        
        # Crear el juego
        juego_data = {
            'titulo': request.data.get('titulo'),
            'descripcion': request.data.get('descripcion'),
            'categoria_id': request.data.get('categoria_id'),
            'tipo_juego': request.data.get('tipo_juego'),
            'nivel_dificultad': request.data.get('nivel_dificultad', 'facil'),
            'objetivos_aprendizaje': request.data.get('objetivos_aprendizaje'),
            'habilidades_desarrolla': request.data.get('habilidades_desarrolla', []),
            'edad_minima': request.data.get('edad_minima', 3),
            'edad_maxima': request.data.get('edad_maxima', 12),
            'tiempo_estimado': request.data.get('tiempo_estimado', 5),
            'configuracion': request.data.get('configuracion', {}),
            'creado_por': profesor
        }
        
        juego = JuegoEducativo.objects.create(**juego_data)
        
        return Response({
            'mensaje': 'Juego educativo creado exitosamente',
            'juego': {
                'id': juego.id,
                'titulo': juego.titulo,
                'tipo_juego': juego.tipo_juego,
                'nivel_dificultad': juego.nivel_dificultad
            }
        }, status=status.HTTP_201_CREATED)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def iniciar_partida_juego(request):
    """Iniciar una nueva partida de juego para un estudiante"""
    user_id = request.data.get('user_id')
    juego_id = request.data.get('juego_id')
    actividad_asignada_id = request.data.get('actividad_asignada_id')  # Opcional
    
    if not all([user_id, juego_id]):
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Verificar que el usuario sea estudiante
        estudiante = Usuario.objects.get(id=user_id)
        if estudiante.rol != 'estudiante':
            return Response({'mensaje': 'Solo los estudiantes pueden jugar'}, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar que el juego existe
        juego = JuegoEducativo.objects.get(id=juego_id, activo=True)
        
        # Verificar actividad asignada si se proporciona
        actividad_asignada = None
        if actividad_asignada_id:
            actividad_asignada = AsignacionActividad.objects.get(
                id=actividad_asignada_id,
                estudiante=estudiante
            )
        
        # Crear nueva partida
        partida = PartidaJuego.objects.create(
            juego=juego,
            estudiante=estudiante,
            actividad_asignada=actividad_asignada,
            estado='iniciada'
        )
        
        # Incrementar contador de veces jugado
        juego.veces_jugado += 1
        juego.save()
        
        return Response({
            'mensaje': 'Partida iniciada exitosamente',
            'partida': {
                'id': partida.id,
                'juego_titulo': juego.titulo,
                'fecha_inicio': partida.fecha_inicio,
                'configuracion_juego': juego.configuracion
            }
        }, status=status.HTTP_201_CREATED)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except JuegoEducativo.DoesNotExist:
        return Response({'mensaje': 'Juego no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except AsignacionActividad.DoesNotExist:
        return Response({'mensaje': 'Actividad asignada no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def finalizar_partida_juego(request):
    """Finalizar una partida y guardar resultados"""
    partida_id = request.data.get('partida_id')
    puntuacion = request.data.get('puntuacion', 0)
    aciertos = request.data.get('aciertos', 0)
    errores = request.data.get('errores', 0)
    tiempo_jugado = request.data.get('tiempo_jugado', 0)
    datos_partida = request.data.get('datos_partida', {})
    
    if not partida_id:
        return Response({'mensaje': 'ID de partida requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        partida = PartidaJuego.objects.get(id=partida_id)
        
        # Actualizar datos de la partida
        partida.estado = 'completada'
        partida.fecha_fin = timezone.now()
        partida.puntuacion = puntuacion
        partida.aciertos = aciertos
        partida.errores = errores
        partida.tiempo_jugado = tiempo_jugado
        partida.datos_partida = datos_partida
        partida.save()
        
        # Actualizar estadísticas del juego
        juego = partida.juego
        partidas_completadas = PartidaJuego.objects.filter(
            juego=juego, 
            estado='completada'
        )
        
        if partidas_completadas.exists():
            promedio = partidas_completadas.aggregate(
                promedio=models.Avg('puntuacion')
            )['promedio']
            juego.puntuacion_promedio = promedio or 0
            juego.save()
        
        return Response({
            'mensaje': 'Partida finalizada exitosamente',
            'resultados': {
                'puntuacion': partida.puntuacion,
                'porcentaje_aciertos': partida.porcentaje_aciertos,
                'tiempo_formateado': partida.tiempo_formateado,
                'estado': 'completada'
            }
        }, status=status.HTTP_200_OK)
        
    except PartidaJuego.DoesNotExist:
        return Response({'mensaje': 'Partida no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'mensaje': f'Error interno: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============= SISTEMA DE PERMISOS BASADO EN ROLES =============

def verificar_permisos(roles_permitidos):
    """
    Decorador para verificar permisos basados en roles
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user_id = request.data.get('user_id') or request.GET.get('user_id')
            if not user_id:
                return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
            
            try:
                usuario = Usuario.objects.get(id=user_id)
                if usuario.rol not in roles_permitidos:
                    return Response({'mensaje': 'No tienes permisos para realizar esta acción'}, status=status.HTTP_403_FORBIDDEN)
                
                # Agregar usuario al request para uso posterior
                request.usuario = usuario
                return func(request, *args, **kwargs)
                
            except Usuario.DoesNotExist:
                return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return wrapper
    return decorator

# ============= GESTIÓN DE USUARIOS =============

@api_view(['GET'])
@verificar_permisos(['profesor', 'administrador'])
def listar_usuarios_por_rol(request):
    """
    Lista usuarios según el rol del solicitante
    Profesor: Solo puede ver estudiantes
    Administrador: Puede ver todos los usuarios
    """
    if request.usuario.rol == 'profesor':
        usuarios = Usuario.objects.filter(rol='estudiante').order_by('username')
    else:  # administrador
        usuarios = Usuario.objects.all().order_by('rol', 'username')
    
    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@verificar_permisos(['profesor', 'administrador'])
def crear_usuario_con_permisos(request):
    """
    Crear nuevo usuario
    Profesor: Solo puede crear estudiantes
    Administrador: Puede crear cualquier tipo de usuario
    """
    rol_solicitado = request.data.get('rol', 'estudiante')
    
    # Verificar permisos según rol
    if request.usuario.rol == 'profesor' and rol_solicitado != 'estudiante':
        return Response({'mensaje': 'Los profesores solo pueden crear estudiantes'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT', 'DELETE'])
@verificar_permisos(['profesor', 'administrador'])
def gestionar_usuario_especifico(request, user_id):
    """
    Editar o eliminar usuario
    Profesor: Solo puede gestionar estudiantes
    Administrador: Puede gestionar cualquier usuario
    """
    try:
        usuario_objetivo = Usuario.objects.get(id=user_id)
        
        # Verificar permisos
        if request.usuario.rol == 'profesor':
            if usuario_objetivo.rol != 'estudiante':
                return Response({'mensaje': 'Los profesores solo pueden gestionar estudiantes'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            # Editar usuario
            serializer = UsuarioSerializer(usuario_objetivo, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            # Eliminar usuario
            usuario_objetivo.delete()
            return Response({'mensaje': 'Usuario eliminado exitosamente'}, status=status.HTTP_200_OK)
            
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ============= GESTIÓN DE CURSOS CON PERMISOS =============

@api_view(['PUT', 'DELETE'])
@verificar_permisos(['profesor', 'administrador'])
def gestionar_curso_especifico(request, curso_id):
    """
    Editar o eliminar curso
    Profesor: Solo sus propios cursos
    Administrador: Cualquier curso
    """
    try:
        curso = Curso.objects.get(id=curso_id)
        
        # Verificar permisos
        if request.usuario.rol == 'profesor' and curso.profesor != request.usuario:
            return Response({'mensaje': 'Solo puedes gestionar tus propios cursos'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            serializer = CursoSerializer(curso, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            curso.delete()
            return Response({'mensaje': 'Curso eliminado exitosamente'}, status=status.HTTP_200_OK)
            
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ============= GESTIÓN DE ACTIVIDADES CON PERMISOS =============

@api_view(['PUT', 'DELETE'])
@verificar_permisos(['profesor', 'administrador'])
def gestionar_actividad_especifica(request, actividad_id):
    """
    Editar o eliminar actividad
    Profesor: Solo actividades de sus cursos
    Administrador: Cualquier actividad
    """
    try:
        actividad = Actividad.objects.get(id=actividad_id)
        
        # Verificar permisos
        if request.usuario.rol == 'profesor':
            if actividad.curso.profesor != request.usuario:
                return Response({'mensaje': 'Solo puedes gestionar actividades de tus cursos'}, status=status.HTTP_403_FORBIDDEN)
        
        if request.method == 'PUT':
            serializer = ActividadSerializer(actividad, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            actividad.delete()
            return Response({'mensaje': 'Actividad eliminada exitosamente'}, status=status.HTTP_200_OK)
            
    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

# ============= GESTIÓN DE ESTUDIANTES EN CURSOS =============

@api_view(['POST'])
@verificar_permisos(['profesor', 'administrador'])
def agregar_estudiante_a_curso(request):
    """
    Agregar estudiante a un curso
    """
    estudiante_id = request.data.get('estudiante_id')
    curso_id = request.data.get('curso_id')
    
    if not estudiante_id or not curso_id:
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        estudiante = Usuario.objects.get(id=estudiante_id, rol='estudiante')
        curso = Curso.objects.get(id=curso_id)
        
        # Verificar permisos
        if request.usuario.rol == 'profesor' and curso.profesor != request.usuario:
            return Response({'mensaje': 'Solo puedes agregar estudiantes a tus cursos'}, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar si ya está inscrito
        if EstudianteCurso.objects.filter(estudiante=estudiante, curso=curso).exists():
            return Response({'mensaje': 'El estudiante ya está inscrito en este curso'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear inscripción
        inscripcion = EstudianteCurso.objects.create(estudiante=estudiante, curso=curso)
        serializer = EstudianteCursoSerializer(inscripcion)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@verificar_permisos(['profesor', 'administrador'])
def remover_estudiante_de_curso(request, inscripcion_id):
    """
    Remover estudiante de un curso
    """
    try:
        inscripcion = EstudianteCurso.objects.get(id=inscripcion_id)
        
        # Verificar permisos
        if request.usuario.rol == 'profesor' and inscripcion.curso.profesor != request.usuario:
            return Response({'mensaje': 'Solo puedes remover estudiantes de tus cursos'}, status=status.HTTP_403_FORBIDDEN)
        
        inscripcion.delete()
        return Response({'mensaje': 'Estudiante removido del curso exitosamente'}, status=status.HTTP_200_OK)
        
    except EstudianteCurso.DoesNotExist:
        return Response({'mensaje': 'Inscripción no encontrada'}, status=status.HTTP_404_NOT_FOUND)

# ============= GESTIÓN DE PROFESORES EN CURSOS (Solo Administrador) =============

@api_view(['POST'])
@verificar_permisos(['administrador'])
def asignar_profesor_a_curso(request, curso_id):
    """
    Asignar profesor a un curso (Solo administrador)
    """
    profesor_id = request.data.get('profesor_id')
    
    if not profesor_id:
        return Response({'mensaje': 'ID del profesor requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        curso = Curso.objects.get(id=curso_id)
        profesor = Usuario.objects.get(id=profesor_id, rol='profesor')
        
        curso.profesor = profesor
        curso.save()
        
        serializer = CursoSerializer(curso)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Profesor no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ============= PERFIL DE USUARIO =============

@api_view(['GET', 'PUT'])
def gestionar_perfil_propio(request):
    """
    Ver y editar el propio perfil
    """
    user_id = request.data.get('user_id') or request.GET.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        usuario = Usuario.objects.get(id=user_id)
        
        if request.method == 'GET':
            serializer = UsuarioSerializer(usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        elif request.method == 'PUT':
            # Solo permitir editar ciertos campos del propio perfil
            campos_permitidos = ['nombre_completo', 'email']
            data_filtrada = {k: v for k, v in request.data.items() if k in campos_permitidos}
            
            serializer = UsuarioSerializer(usuario, data=data_filtrada, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ============= SISTEMA DE ACTIVIDADES PARA ESTUDIANTES =============

@api_view(['GET'])
def obtener_actividades_estudiante(request):
    """
    Obtener todas las actividades asignadas a un estudiante
    Solo estudiantes autenticados pueden acceder a sus actividades
    """
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Verificar que el usuario que hace la petición es el mismo estudiante o un profesor/admin
    request_user_id = request.user.id if request.user.is_authenticated else None
    if request_user_id and request_user_id != int(user_id):
        # Si no es el mismo estudiante, verificar si es profesor/admin del curso
        try:
            request_user = Usuario.objects.get(id=request_user_id)
            if request_user.rol not in ['profesor', 'administrador']:
                return Response({'mensaje': 'No tienes permisos para ver estas actividades'}, status=status.HTTP_403_FORBIDDEN)
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        
        # Obtener asignaciones específicas del estudiante
        asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related('actividad', 'actividad__curso')
        
        # Crear lista de actividades asignadas con información adicional
        actividades_data = []
        for asignacion in asignaciones:
            actividad = asignacion.actividad
            
            actividad_data = ActividadSerializer(actividad).data
            actividad_data['progreso'] = {
                'completada': asignacion.estado in ['completada', 'revisada', 'calificada'],
                'fecha_completado': asignacion.fecha_entrega,
                'puntuacion': asignacion.calificacion,
                'estado': asignacion.estado,
                'comentarios': asignacion.comentarios_estudiante,
                'fecha_asignacion': asignacion.fecha_asignacion
            }
            
            # Calcular estado de la actividad
            if actividad.fecha_limite:
                ahora = timezone.now().date()
                if actividad.fecha_limite < ahora:
                    actividad_data['estado_tiempo'] = 'vencida'
                elif (actividad.fecha_limite - ahora).days <= 3:
                    actividad_data['estado_tiempo'] = 'por_vencer'
                else:
                    actividad_data['estado_tiempo'] = 'activa'
            else:
                actividad_data['estado_tiempo'] = 'sin_limite'
            
            actividades_data.append(actividad_data)
        
        return Response(actividades_data, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def iniciar_actividad_estudiante(request):
    """
    Marcar que un estudiante ha iniciado una actividad
    Solo el estudiante puede iniciar sus propias actividades
    """
    user_id = request.data.get('user_id')
    actividad_id = request.data.get('actividad_id')
    
    if not user_id or not actividad_id:
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    # El user_id del request es suficiente para la autorización en este caso
    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        actividad = Actividad.objects.get(id=actividad_id)
        
        # Verificar que el estudiante esté inscrito en el curso de la actividad
        if not EstudianteCurso.objects.filter(estudiante=estudiante, curso=actividad.curso).exists():
            return Response({'mensaje': 'No tienes acceso a esta actividad'}, status=status.HTTP_403_FORBIDDEN)
        
        # Crear o actualizar asignación
        asignacion, created = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': actividad.creado_por or actividad.curso.profesor,
                'estado': 'en_progreso'
            }
        )
        
        if not created and asignacion.estado == 'asignada':
            asignacion.estado = 'en_progreso'
            asignacion.save()
        
        return Response({
            'mensaje': 'Actividad iniciada exitosamente',
            'progreso': {
                'estado': asignacion.estado,
                'fecha_asignacion': asignacion.fecha_asignacion
            }
        }, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def completar_actividad_estudiante(request):
    """
    Marcar una actividad como completada por el estudiante
    Solo el estudiante puede completar sus propias actividades
    """
    user_id = request.data.get('user_id')
    actividad_id = request.data.get('actividad_id')
    puntuacion = request.data.get('puntuacion', 0)
    tiempo_empleado = request.data.get('tiempo_empleado', 0)  # en minutos
    respuestas_detalle = request.data.get('respuestas_detalle', [])  # Respuestas individuales
    
    if not user_id or not actividad_id:
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        actividad = Actividad.objects.get(id=actividad_id)
        
        # Verificar que el estudiante esté inscrito en el curso
        if not EstudianteCurso.objects.filter(estudiante=estudiante, curso=actividad.curso).exists():
            return Response({'mensaje': 'No tienes acceso a esta actividad'}, status=status.HTTP_403_FORBIDDEN)
        
        # Verificar si la actividad no está vencida (opcional, permitir completar aunque esté vencida)
        if actividad.fecha_limite and actividad.fecha_limite < timezone.now().date():
            # Permitir completar pero marcar como tardía
            es_tardia = True
        else:
            es_tardia = False
        
        # Actualizar asignación
        asignacion, created = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': actividad.creado_por or actividad.curso.profesor,
                'estado': 'completada'
            }
        )
        
        asignacion.estado = 'completada'
        asignacion.fecha_entrega = timezone.now()
        asignacion.calificacion = puntuacion
        if es_tardia:
            asignacion.comentarios_estudiante = f"Entregada tarde. Tiempo empleado: {tiempo_empleado} minutos"
        else:
            asignacion.comentarios_estudiante = f"Tiempo empleado: {tiempo_empleado} minutos"
        asignacion.save()
        
        # Registrar evento
        registrar_evento_actividad(
            actividad_id=actividad_id,
            estudiante_id=user_id,
            evento_tipo='completada',
            datos_adicionales={
                'puntuacion': puntuacion,
                'tiempo_empleado': tiempo_empleado,
                'es_tardia': es_tardia
            }
        )
        
        # Preparar datos para enviar al webhook
        actividad_data = {
            'estudiante_id': estudiante.id,
            'estudiante_nombre': estudiante.nombre_completo,
            'estudiante_email': estudiante.email,
            'actividad_id': actividad.id,
            'actividad_titulo': actividad.titulo,
            'actividad_tipo': actividad.tipo,
            'curso_id': actividad.curso.id,
            'curso_nombre': actividad.curso.nombre,
            'puntuacion': puntuacion,
            'tiempo_empleado': tiempo_empleado,
            'fecha_entrega': asignacion.fecha_entrega,
            'estado': asignacion.estado,
            'es_tardia': es_tardia,
            'respuestas_detalle': respuestas_detalle  # Incluir detalle de respuestas
        }
        
        # Enviar a webhook de n8n
        webhook_result = enviar_resultado_actividad_a_n8n(actividad_data)
        webhook_info = {
            'enviado': webhook_result['success'],
            'mensaje': webhook_result['message'],
            'codigo': webhook_result.get('response_code', 0)
        }
        
        return Response({
            'mensaje': 'Actividad completada exitosamente',
            'progreso': {
                'completada': True,
                'fecha_completado': asignacion.fecha_entrega,
                'puntuacion': asignacion.calificacion,
                'tiempo_empleado': tiempo_empleado,
                'es_tardia': es_tardia,
                'estado': asignacion.estado
            },
            'webhook': webhook_info
        }, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Actividad.DoesNotExist:
        return Response({'mensaje': 'Actividad no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def obtener_estadisticas_estudiante(request):
    """
    Obtener estadísticas del progreso del estudiante
    El estudiante puede ver sus propias estadísticas, profesores pueden ver estadísticas de estudiantes de sus cursos
    """
    user_id = request.GET.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    # Verificar que el usuario que hace la petición es el mismo estudiante o un profesor/admin
    request_user_id = request.user.id if request.user.is_authenticated else None

    if request_user_id and request_user_id != int(user_id):
        # Si no es el mismo estudiante, verificar si es profesor/admin
        try:
            request_user = Usuario.objects.get(id=request_user_id)
            if request_user.rol not in ['profesor', 'administrador']:
                return Response({'mensaje': 'Solo puedes ver tus propias estadísticas'}, status=status.HTTP_403_FORBIDDEN)
            # Si es profesor/admin, continuar con la lógica normal
        except Usuario.DoesNotExist:
            return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')
        
        # Obtener asignaciones específicas del estudiante
        asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related('actividad')
        actividades_ids = [a.actividad.id for a in asignaciones]
        
        # Estadísticas generales
        total_actividades = len(actividades_ids)
        actividades_completadas = asignaciones.filter(estado__in=['completada', 'revisada', 'calificada']).count()
        
        actividades_pendientes = total_actividades - actividades_completadas
        
        # Actividades por vencer (próximos 7 días)
        fecha_limite = timezone.now().date() + timezone.timedelta(days=7)
        actividades_por_vencer = asignaciones.filter(
            actividad__fecha_limite__lte=fecha_limite,
            actividad__fecha_limite__gte=timezone.now().date(),
            estado__in=['asignada', 'en_progreso']
        ).count()
        
        # Actividades vencidas
        actividades_vencidas = asignaciones.filter(
            actividad__fecha_limite__lt=timezone.now().date(),
            estado__in=['asignada', 'en_progreso']
        ).count()
        
        # Puntuación promedio
        puntuacion_promedio = asignaciones.filter(
            estado__in=['completada', 'revisada', 'calificada'],
            calificacion__isnull=False
        ).aggregate(promedio=models.Avg('calificacion'))['promedio'] or 0
        
        return Response({
            'actividades_completadas': actividades_completadas,
            'actividades_pendientes': actividades_pendientes,
            'actividades_por_vencer': actividades_por_vencer,
            'actividades_vencidas': actividades_vencidas,
            'puntuacion_promedio': round(puntuacion_promedio, 2),
            'porcentaje_completado': round((actividades_completadas / total_actividades * 100) if total_actividades > 0 else 0, 2)
        }, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def listar_estudiantes_curso(request):
    """
    Listar estudiantes inscritos en un curso específico
    """
    curso_id = request.GET.get('curso_id')
    user_id = request.GET.get('user_id')

    if not curso_id or not user_id:
        return Response({'mensaje': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(id=user_id)

        # Verificar permisos
        if usuario.rol == 'administrador':
            pass  # Admin puede ver cualquier curso
        elif usuario.rol == 'profesor':
            curso = Curso.objects.get(id=curso_id)
            if curso.profesor != usuario:
                return Response({'mensaje': 'No tienes permisos para ver este curso'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'mensaje': 'No tienes permisos para esta acción'}, status=status.HTTP_403_FORBIDDEN)

        curso = Curso.objects.get(id=curso_id)
        estudiantes = EstudianteCurso.objects.filter(curso=curso).select_related('estudiante')

        estudiantes_data = []
        for inscripcion in estudiantes:
            estudiantes_data.append({
                'id': inscripcion.id,
                'estudiante': {
                    'id': inscripcion.estudiante.id,
                    'username': inscripcion.estudiante.username,
                    'nombre_completo': inscripcion.estudiante.nombre_completo,
                    'email': inscripcion.estudiante.email
                },
                'fecha_inscripcion': inscripcion.fecha_inscripcion
            })

        return Response(estudiantes_data, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def agregar_estudiante_a_curso(request):
    """
    Agregar un estudiante a un curso
    """
    estudiante_id = request.data.get('estudiante_id')
    curso_id = request.data.get('curso_id')
    user_id = request.data.get('user_id')

    if not all([estudiante_id, curso_id, user_id]):
        return Response({'mensaje': 'Faltan datos requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(id=user_id)

        # Verificar permisos
        if usuario.rol == 'administrador':
            pass  # Admin puede agregar a cualquier curso
        elif usuario.rol == 'profesor':
            curso = Curso.objects.get(id=curso_id)
            if curso.profesor != usuario:
                return Response({'mensaje': 'No tienes permisos para gestionar este curso'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'mensaje': 'No tienes permisos para esta acción'}, status=status.HTTP_403_FORBIDDEN)

        estudiante = Usuario.objects.get(id=estudiante_id, rol='estudiante')
        curso = Curso.objects.get(id=curso_id)

        # Verificar si ya está inscrito
        if EstudianteCurso.objects.filter(estudiante=estudiante, curso=curso).exists():
            return Response({'mensaje': 'El estudiante ya está inscrito en este curso'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear inscripción
        EstudianteCurso.objects.create(estudiante=estudiante, curso=curso)

        return Response({'mensaje': 'Estudiante agregado al curso exitosamente'}, status=status.HTTP_201_CREATED)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
def remover_estudiante_de_curso(request, inscripcion_id):
    """
    Remover un estudiante de un curso
    """
    user_id = request.GET.get('user_id')

    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        usuario = Usuario.objects.get(id=user_id)

        # Obtener inscripción
        inscripcion = EstudianteCurso.objects.get(id=inscripcion_id)

        # Verificar permisos
        if usuario.rol == 'administrador':
            pass  # Admin puede remover de cualquier curso
        elif usuario.rol == 'profesor':
            if inscripcion.curso.profesor != usuario:
                return Response({'mensaje': 'No tienes permisos para gestionar este curso'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'mensaje': 'No tienes permisos para esta acción'}, status=status.HTTP_403_FORBIDDEN)

        inscripcion.delete()

        return Response({'mensaje': 'Estudiante removido del curso exitosamente'}, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except EstudianteCurso.DoesNotExist:
        return Response({'mensaje': 'Inscripción no encontrada'}, status=status.HTTP_404_NOT_FOUND)

# ============= FUNCIONES FALTANTES =============

@api_view(['POST'])
def asignar_actividad_curso(request):
    """
    Asignar actividades a estudiantes de un curso completo
    """
    curso_id = request.data.get('curso_id')
    actividad_ids = request.data.get('actividad_ids', [])
    user_id = request.data.get('user_id')

    print(f"DEBUG: Datos recibidos - curso_id={curso_id}, actividad_ids={actividad_ids}, user_id={user_id}")

    # Validar que todos los campos requeridos estén presentes y no vacíos
    if not curso_id or not user_id or not actividad_ids or not isinstance(actividad_ids, list):
        error_details = {
            'curso_id': 'Falta o inválido' if not curso_id else None,
            'actividad_ids': 'Falta o inválido' if not actividad_ids or not isinstance(actividad_ids, list) else None,
            'user_id': 'Falta o inválido' if not user_id else None
        }
        error_details = {k: v for k, v in error_details.items() if v is not None}
        print(f"DEBUG: Validación fallida - {error_details}")
        return Response({'mensaje': 'Faltan datos requeridos', 'detalles': error_details}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(id=user_id)
        curso = Curso.objects.get(id=curso_id)

        print(f"DEBUG: Usuario encontrado - {usuario.username} (rol: {usuario.rol})")
        print(f"DEBUG: Curso encontrado - {curso.nombre} (profesor: {curso.profesor})")

        # Verificar permisos
        if usuario.rol == 'administrador':
            pass
        elif usuario.rol == 'profesor':
            if curso.profesor != usuario:
                print(f"DEBUG: Error de permisos - profesor {usuario.username} no es dueño del curso {curso.nombre}")
                return Response({'mensaje': 'No tienes permisos para gestionar este curso'}, status=status.HTTP_403_FORBIDDEN)
        else:
            print(f"DEBUG: Error de permisos - usuario {usuario.username} no tiene rol válido")
            return Response({'mensaje': 'No tienes permisos para esta acción'}, status=status.HTTP_403_FORBIDDEN)

        # Obtener estudiantes del curso
        estudiantes_curso = EstudianteCurso.objects.filter(curso=curso)
        print(f"DEBUG: Estudiantes en el curso - {estudiantes_curso.count()}")

        actividades_asignadas = 0
        for actividad_id in actividad_ids:
            try:
                actividad = Actividad.objects.get(id=actividad_id, curso=curso)
                print(f"DEBUG: Procesando actividad - {actividad.titulo} (ID: {actividad.id})")

                for estudiante_curso in estudiantes_curso:
                    # Crear asignación si no existe
                    asignacion, created = AsignacionActividad.objects.get_or_create(
                        actividad=actividad,
                        estudiante=estudiante_curso.estudiante,
                        defaults={
                            'profesor': usuario,
                            'estado': 'asignada'
                        }
                    )
                    if not created:
                        asignacion.estado = 'asignada'
                        asignacion.save()

                    actividades_asignadas += 1

            except Actividad.DoesNotExist:
                print(f"DEBUG: Actividad no encontrada - ID: {actividad_id}")
                continue

        print(f"DEBUG: Actividades asignadas exitosamente - {actividades_asignadas}")
        return Response({
            'mensaje': f'Se asignaron {actividades_asignadas} actividades a estudiantes del curso'
        }, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        print(f"DEBUG: Usuario no encontrado - ID: {user_id}")
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        print(f"DEBUG: Curso no encontrado - ID: {curso_id}")
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def actividades_asignadas_estudiante(request):
    """
    Obtener actividades asignadas directamente a un estudiante
    """
    user_id = request.GET.get('user_id')

    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        estudiante = Usuario.objects.get(id=user_id, rol='estudiante')

        asignaciones = AsignacionActividad.objects.filter(estudiante=estudiante).select_related('actividad', 'actividad__curso')

        actividades_data = []
        for asignacion in asignaciones:
            actividades_data.append({
                'id': asignacion.id,
                'actividad': {
                    'id': asignacion.actividad.id,
                    'titulo': asignacion.actividad.titulo,
                    'descripcion': asignacion.actividad.descripcion,
                    'tipo': asignacion.actividad.tipo,
                    'fecha_limite': asignacion.actividad.fecha_limite,
                    'curso': asignacion.actividad.curso.nombre if asignacion.actividad.curso else None
                },
                'estado': asignacion.estado,
                'fecha_asignacion': asignacion.fecha_asignacion,
                'fecha_entrega': asignacion.fecha_entrega,
                'calificacion': asignacion.calificacion,
                'comentarios_profesor': asignacion.comentarios_profesor,
                'comentarios_estudiante': asignacion.comentarios_estudiante
            })

        return Response(actividades_data, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Estudiante no encontrado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def actividades_curso_profesor(request):
    """
    Obtener actividades de un curso para el profesor (con estadísticas de estudiantes)
    """
    curso_id = request.GET.get('curso_id')
    user_id = request.GET.get('user_id')

    if not all([curso_id, user_id]):
        return Response({'mensaje': 'Faltan parámetros requeridos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(id=user_id)
        curso = Curso.objects.get(id=curso_id)

        # Verificar permisos
        if usuario.rol == 'administrador':
            pass
        elif usuario.rol == 'profesor':
            if curso.profesor != usuario:
                return Response({'mensaje': 'No tienes permisos para ver este curso'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'mensaje': 'No tienes permisos para esta acción'}, status=status.HTTP_403_FORBIDDEN)

        actividades = Actividad.objects.filter(curso=curso).order_by('-fecha_creacion')

        actividades_data = []
        for actividad in actividades:
            # Obtener estadísticas de estudiantes
            asignaciones = AsignacionActividad.objects.filter(actividad=actividad)

            actividades_data.append({
                'id': actividad.id,
                'titulo': actividad.titulo,
                'descripcion': actividad.descripcion,
                'tipo': actividad.tipo,
                'fecha_limite': actividad.fecha_limite,
                'estado': actividad.estado,
                'estadisticas': {
                    'total_estudiantes': asignaciones.count(),
                    'completadas': asignaciones.filter(estado__in=['completada', 'revisada', 'calificada']).count(),
                    'pendientes': asignaciones.filter(estado='asignada').count(),
                    'en_progreso': asignaciones.filter(estado='en_progreso').count()
                }
            })

        return Response(actividades_data, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Curso.DoesNotExist:
        return Response({'mensaje': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)