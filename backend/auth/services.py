"""
Servicios de autenticación — EduNúñez.

Usa djangorestframework-simplejwt para emisión de tokens JWT con
rotación de refresh y blacklist al hacer logout/rotación.
PyJWT ya no se usa directamente aquí.
"""
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape
from django.utils import timezone
from datetime import timedelta

from rest_framework_simplejwt.tokens import RefreshToken

from .models import MagicLinkToken

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _build_token_payload(usuario, refresh: RefreshToken) -> dict:
    """
    Construye el dict de respuesta estándar que recibe el frontend tras login.
    Incluye access, refresh y los datos básicos del usuario.
    """
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "usuario_id": usuario.pk,
        "username": usuario.username,
        "email": usuario.email,
        "nombre_completo": usuario.nombre_completo,
        "rol": usuario.rol,
    }


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

def generar_tokens(usuario) -> dict:
    """
    Genera un par access/refresh para el usuario dado y retorna el payload
    de respuesta estándar.

    Usa RefreshToken.for_user() de simplejwt que agrega las claims del
    modelo automáticamente y respeta SIMPLE_JWT en settings.
    """
    refresh = RefreshToken.for_user(usuario)
    return _build_token_payload(usuario, refresh)


# Alias de compatibilidad — las vistas antiguas llaman a autenticar_usuario.
def autenticar_usuario(request, email: str, password: str) -> dict:
    """
    Autentica al usuario con email + contraseña y retorna el payload de tokens.

    Raises:
        ValueError: Si faltan credenciales o son incorrectas.
    """
    if not email or not password:
        raise ValueError("Faltan datos")

    try:
        usuario = User.objects.get(email__iexact=email.strip())
    except User.DoesNotExist:
        # Mensaje genérico para no confirmar existencia del email.
        raise ValueError("Usuario o contraseña incorrectos")

    usuario_autenticado = authenticate(request, username=usuario.username, password=password)
    if usuario_autenticado is None:
        raise ValueError("Usuario o contraseña incorrectos")

    return generar_tokens(usuario_autenticado)


# ---------------------------------------------------------------------------
# Magic Link
# ---------------------------------------------------------------------------

def enviar_magic_link(email: str, enlace: str) -> None:
    """Envía el correo con el magic link al usuario."""
    asunto = "Tu acceso seguro a EduNúñez"
    texto = f"Usa este enlace para iniciar sesión en EduNúñez: {enlace}"
    html = (
        "<p>Usa este enlace para iniciar sesión en EduNúñez:</p>"
        f'<p><a href="{escape(enlace)}">{escape(enlace)}</a></p>'
    )
    mensaje = EmailMultiAlternatives(
        subject=asunto,
        body=texto,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@edununez.local"),
        to=[email],
    )
    mensaje.attach_alternative(html, "text/html")
    mensaje.send(fail_silently=False)


def crear_magic_link(email: str) -> dict:
    """
    Crea un MagicLinkToken para el usuario, genera el enlace y envía el correo.

    Raises:
        ValueError: Si el email está vacío o no existe en BD.
    """
    if not email:
        raise ValueError("El email es obligatorio")

    try:
        usuario = User.objects.get(email__iexact=email.strip())
    except User.DoesNotExist:
        raise ValueError("Email no registrado")

    token_obj = MagicLinkToken.objects.create(user=usuario)
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")
    enlace = f"{frontend_url}/verify?token={token_obj.token}"
    enviar_magic_link(usuario.email, enlace)
    return {"mensaje": "Magic link enviado. Revisa tu correo."}


def verificar_magic_link(token: str) -> dict:
    """
    Verifica el token de magic link y, si es válido, emite un par de tokens JWT.

    Raises:
        ValueError: Si el token es inválido, ya fue usado o expiró.
    """
    if not token:
        raise ValueError("Token no enviado")

    try:
        token_obj = MagicLinkToken.objects.select_related("user").get(token=token)
    except (ObjectDoesNotExist, ValueError):
        raise ValueError("Token inválido")

    if token_obj.used:
        raise ValueError("El token ya fue usado")

    expiracion = token_obj.created_at + timedelta(minutes=15)
    if expiracion < timezone.now():
        raise ValueError("Token expirado")

    token_obj.used = True
    token_obj.save(update_fields=["used"])

    # Emitir tokens JWT via simplejwt
    return generar_tokens(token_obj.user)
