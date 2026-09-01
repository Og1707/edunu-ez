"""
Vistas de autenticación y gestión de usuarios — EduNúñez.

Todos los endpoints están anotados con @extend_schema para que
drf-spectacular genere el esquema OpenAPI correctamente.
"""
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers as drf_serializers
from rest_framework import viewsets, permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes, throttle_classes
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from auth.services import autenticar_usuario
from api.throttling import AuthRateThrottle
from ..models import Usuario
from ..permissions import IsAdministrador, IsOwner, IsProfesor
from ..serializers import UsuarioSerializer, LoginResponseSerializer


# ─── Schemas de respuesta reutilizables ──────────────────────────────────────

_login_response_schema = inline_serializer(
    name="LoginResponse",
    fields={
        "access": drf_serializers.CharField(help_text="JWT access token (1 hora de vida)"),
        "refresh": drf_serializers.CharField(help_text="JWT refresh token (7 días de vida)"),
        "usuario_id": drf_serializers.IntegerField(),
        "username": drf_serializers.CharField(),
        "email": drf_serializers.EmailField(),
        "nombre_completo": drf_serializers.CharField(),
        "rol": drf_serializers.ChoiceField(choices=["estudiante", "profesor", "administrador"]),
    },
)

_error_schema = inline_serializer(
    name="ErrorResponse",
    fields={"mensaje": drf_serializers.CharField()},
)


# ─── Vistas ──────────────────────────────────────────────────────────────────

@extend_schema(
    tags=["Autenticación"],
    summary="Registro público de usuario",
    description=(
        "Crea un nuevo usuario con rol **estudiante** forzado. "
        "No es posible crear profesores o administradores desde este endpoint; "
        "usa `/api/usuarios/crear/` con autenticación para eso."
    ),
    request=UsuarioSerializer,
    responses={
        201: UsuarioSerializer,
        400: OpenApiResponse(description="Datos inválidos"),
    },
)
@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
@throttle_classes([AuthRateThrottle])
def registrar_usuario(request):
    """
    Endpoint público para auto-registro de nuevos usuarios con rate limiting.
    Fuerza el rol a 'estudiante' para prevenir escalamiento de privilegios.
    """
    data = request.data.copy()
    data["rol"] = "estudiante"

    serializer = UsuarioSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioViewSet(viewsets.ModelViewSet):
    """ViewSet para operaciones CRUD de Usuario (uso interno/admin)."""

    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]


@extend_schema(
    tags=["Autenticación"],
    summary="Inicio de sesión",
    description=(
        "Autentica al usuario con email y contraseña. "
        "Retorna un par de tokens JWT: **access** (1h) y **refresh** (7d). "
        "El access token se envía en el header `Authorization: Bearer <token>`."
    ),
    request=inline_serializer(
        name="LoginRequest",
        fields={
            "email": drf_serializers.EmailField(),
            "password": drf_serializers.CharField(),
        },
    ),
    responses={
        200: _login_response_schema,
        400: OpenApiResponse(description="Faltan datos"),
        401: OpenApiResponse(description="Credenciales incorrectas"),
    },
    methods=["POST"],
)
@extend_schema(methods=["GET"], exclude=True)  # El GET es legado, no documentar
@api_view(["GET", "POST"])
@authentication_classes([])
@permission_classes([])
@throttle_classes([AuthRateThrottle])
def login_usuario(request):
    """
    Endpoint de inicio de sesión. Retorna access + refresh tokens (simplejwt).
    """
    email = request.data.get("email")
    password = request.data.get("password")

    try:
        payload = autenticar_usuario(request, email, password)
        return Response(payload, status=status.HTTP_200_OK)
    except ValueError as exc:
        code = status.HTTP_400_BAD_REQUEST if str(exc) == "Faltan datos" else status.HTTP_401_UNAUTHORIZED
        return Response({"mensaje": str(exc)}, status=code)


@extend_schema(
    tags=["Usuarios"],
    summary="Listar usuarios por rol",
    description=(
        "Retorna usuarios según el rol del solicitante:\n"
        "- **Profesor**: solo ve estudiantes\n"
        "- **Administrador**: ve todos los usuarios"
    ),
    parameters=[
        OpenApiParameter(
            "rol",
            OpenApiTypes.STR,
            OpenApiParameter.QUERY,
            description="Filtrar por rol (estudiante | profesor | administrador)",
            required=False,
        )
    ],
    responses={
        200: UsuarioSerializer(many=True),
        401: OpenApiResponse(description="No autenticado"),
        403: OpenApiResponse(description="Rol insuficiente"),
    },
)
@api_view(["GET"])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, IsProfesor | IsAdministrador])
def listar_usuarios_por_rol(request):
    """Lista usuarios según el rol del solicitante."""
    usuario = request.user

    if usuario.rol == "profesor":
        usuarios = Usuario.objects.filter(rol="estudiante").order_by("username")
    else:
        usuarios = Usuario.objects.all().order_by("rol", "username")

    serializer = UsuarioSerializer(usuarios, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Usuarios"],
    summary="Crear usuario con permisos",
    description=(
        "Crea un nuevo usuario. "
        "Un **Profesor** solo puede crear estudiantes. "
        "Un **Administrador** puede crear cualquier rol."
    ),
    request=UsuarioSerializer,
    responses={
        201: UsuarioSerializer,
        400: OpenApiResponse(description="Datos inválidos"),
        403: OpenApiResponse(description="Permiso denegado por rol"),
    },
)
@api_view(["POST"])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, IsProfesor | IsAdministrador])
def crear_usuario_con_permisos(request):
    """Crear nuevo usuario respetando restricciones de rol."""
    rol_solicitado = request.data.get("rol", "estudiante")

    if request.user.rol == "profesor" and rol_solicitado != "estudiante":
        return Response(
            {"mensaje": "Los profesores solo pueden crear estudiantes"},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = UsuarioSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Usuarios"],
    summary="Editar o eliminar usuario",
    description=(
        "Edita (PUT) o elimina (DELETE) un usuario por ID. "
        "**Profesor**: solo puede gestionar estudiantes. "
        "**Administrador**: puede gestionar cualquier usuario."
    ),
    request=UsuarioSerializer,
    responses={
        200: UsuarioSerializer,
        404: OpenApiResponse(description="Usuario no encontrado"),
        403: OpenApiResponse(description="Permiso denegado"),
    },
)
@api_view(["PUT", "DELETE"])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, IsProfesor | IsAdministrador])
def gestionar_usuario_especifico(request, user_id):
    """Editar o eliminar un usuario por ID."""
    try:
        usuario_objetivo = Usuario.objects.get(id=user_id)
    except Usuario.DoesNotExist:
        return Response({"mensaje": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.rol == "profesor" and usuario_objetivo.rol != "estudiante":
        return Response(
            {"mensaje": "Los profesores solo pueden gestionar estudiantes"},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "PUT":
        serializer = UsuarioSerializer(usuario_objetivo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    usuario_objetivo.delete()
    return Response({"mensaje": "Usuario eliminado exitosamente"}, status=status.HTTP_200_OK)


@extend_schema(
    tags=["Usuarios"],
    summary="Ver y editar perfil propio",
    description="Permite al usuario autenticado ver (GET) y actualizar (PUT) su propio perfil.",
    request=inline_serializer(
        name="PerfilUpdateRequest",
        fields={
            "nombre_completo": drf_serializers.CharField(required=False),
            "email": drf_serializers.EmailField(required=False),
        },
    ),
    responses={
        200: UsuarioSerializer,
        401: OpenApiResponse(description="No autenticado"),
    },
)
@api_view(["GET", "PUT"])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([permissions.IsAuthenticated, IsOwner])
def gestionar_perfil_propio(request):
    """Ver y editar el propio perfil."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return Response({"mensaje": "Usuario no autenticado"}, status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "GET":
        serializer = UsuarioSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    campos_permitidos = ["nombre_completo", "email"]
    data_filtrada = {k: v for k, v in request.data.items() if k in campos_permitidos}
    serializer = UsuarioSerializer(user, data=data_filtrada, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
