from functools import wraps
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..models import Usuario
from ..serializers import UsuarioSerializer


@api_view(['GET', 'POST'])
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


class UsuarioViewSet(viewsets.ModelViewSet):
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
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'mensaje': 'Faltan datos'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        usuario = Usuario.objects.get(email=email)

        if usuario.check_password(password):
            return Response({
                'mensaje': 'Inicio de sesión exitoso',
                'usuario_id': usuario.id,
                'email': usuario.email,
                'username': usuario.username,
                'nombre_completo': usuario.nombre_completo,
                'rol': usuario.rol
            }, status=status.HTTP_200_OK)
        return Response({'mensaje': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)


def verificar_permisos(roles_permitidos):
    """
    Decorador para verificar permisos basados en roles.
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

                request.usuario = usuario
                return func(request, *args, **kwargs)

            except Usuario.DoesNotExist:
                return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        return wrapper
    return decorator


@api_view(['GET'])
@verificar_permisos(['profesor', 'administrador'])
def listar_usuarios_por_rol(request):
    """
    Lista usuarios según el rol del solicitante.
    Profesor: Solo puede ver estudiantes.
    Administrador: Puede ver todos los usuarios.
    """
    if request.usuario.rol == 'profesor':
        usuarios = Usuario.objects.filter(rol='estudiante').order_by('username')
    else:
        usuarios = Usuario.objects.all().order_by('rol', 'username')

    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@verificar_permisos(['profesor', 'administrador'])
def crear_usuario_con_permisos(request):
    """
    Crear nuevo usuario.
    Profesor: Solo puede crear estudiantes.
    Administrador: Puede crear cualquier tipo de usuario.
    """
    rol_solicitado = request.data.get('rol', 'estudiante')

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
    Editar o eliminar usuario.
    Profesor: Solo puede gestionar estudiantes.
    Administrador: Puede gestionar cualquier usuario.
    """
    try:
        usuario_objetivo = Usuario.objects.get(id=user_id)

        if request.usuario.rol == 'profesor' and usuario_objetivo.rol != 'estudiante':
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
def gestionar_perfil_propio(request):
    """
    Ver y editar el propio perfil.
    """
    user_id = request.data.get('user_id') or request.GET.get('user_id')
    if not user_id:
        return Response({'mensaje': 'Usuario no autenticado'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        usuario = Usuario.objects.get(id=user_id)

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

    except Usuario.DoesNotExist:
        return Response({'mensaje': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
