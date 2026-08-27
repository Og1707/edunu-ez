from rest_framework import viewsets, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from auth.services import autenticar_usuario
from ..models import Usuario
from ..permissions import IsAdministrador, IsOwner, IsProfesor
from ..serializers import UsuarioSerializer


@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def registrar_usuario(request):
    """
    Endpoint público para auto-registro de nuevos usuarios.
    Fuerza el rol a 'estudiante' para prevenir escalamiento de privilegios.
    Para crear profesores/administradores, usar el endpoint /api/usuarios/crear/ con autenticación.
    """
    data = request.data.copy()
    # Forzar rol estudiante en registro público para prevenir escalamiento de privilegios
    data['rol'] = 'estudiante'

    serializer = UsuarioSerializer(data=data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD de Usuario.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET', 'POST'])
@authentication_classes([])
@permission_classes([])
def login_usuario(request):
    """
    Endpoint para iniciar sesión de un usuario.
    Espera un JSON con 'email' y 'password'.
    """
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        payload = autenticar_usuario(request, email, password)
        return Response(payload, status=status.HTTP_200_OK)
    except ValueError as exc:
        status_code = status.HTTP_400_BAD_REQUEST if str(exc) == 'Faltan datos' else status.HTTP_401_UNAUTHORIZED
        return Response({'mensaje': str(exc)}, status=status_code)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, IsProfesor | IsAdministrador])
def listar_usuarios_por_rol(request):
    """
    Lista usuarios según el rol del solicitante.

    Permisos:
        - Profesor: Solo puede ver estudiantes
        - Administrador: Puede ver todos los usuarios

    Returns:
        Response: JSON array de usuarios serializado
        - Status 200: Éxito
        - Status 401: No autenticado
        - Status 403: Rol insuficiente
    """
    usuario = request.user

    if usuario.rol == 'profesor':
        usuarios = Usuario.objects.filter(rol='estudiante').order_by('username')
    else:
        usuarios = Usuario.objects.all().order_by('rol', 'username')

    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, IsProfesor | IsAdministrador])
def crear_usuario_con_permisos(request):
    """
    Crear nuevo usuario.
    Profesor: Solo puede crear estudiantes.
    Administrador: Puede crear cualquier tipo de usuario.
    """
    rol_solicitado = request.data.get('rol', 'estudiante')

    if request.user.rol == 'profesor' and rol_solicitado != 'estudiante':
        return Response({'mensaje': 'Los profesores solo pueden crear estudiantes'}, status=status.HTTP_403_FORBIDDEN)

    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, IsProfesor | IsAdministrador])
def gestionar_usuario_especifico(request, user_id):
    """
    Editar o eliminar usuario.
    Profesor: Solo puede gestionar estudiantes.
    Administrador: Puede gestionar cualquier usuario.
    """
    try:
        usuario_objetivo = Usuario.objects.get(id=user_id)

        if request.user.rol == 'profesor' and usuario_objetivo.rol != 'estudiante':
            return Response({'mensaje': 'Los profesores solo pueden gestionar estudiantes'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'PUT':
            serializer = UsuarioSerializer(usuario_objetivo, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            usuario_objetivo.delete()
            return Response({'mensaje': 'Usuario eliminado exitosamente'}, status=status.HTTP_200_OK)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'PUT'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, IsOwner])
def gestionar_perfil_propio(request):
    """
    Ver y editar el propio perfil.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    usuario = user

    if request.method == 'GET':
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        campos_permitidos = ['nombre_completo', 'email']
        data_filtrada = {k: v for k, v in request.data.items() if k in campos_permitidos}
        serializer = UsuarioSerializer(usuario, data=data_filtrada, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
