import jwt
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape
from django.utils import timezone
from .models import MagicLinkToken


User = get_user_model()


def generar_jwt(usuario):
    payload = {
        'user_id': usuario.pk,
        'email': usuario.email,
        'exp': timezone.now() + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token if isinstance(token, str) else token.decode('utf-8')


def validar_jwt(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError('Token expirado')
    except jwt.InvalidTokenError:
        raise ValueError('Token inválido')

    try:
        return User.objects.get(pk=payload.get('user_id'))
    except User.DoesNotExist:
        raise ValueError('Usuario no encontrado')


def autenticar_usuario(request, email, password):
    if not email or not password:
        raise ValueError('Faltan datos')

    try:
        usuario = User.objects.get(email__iexact=email.strip())
    except User.DoesNotExist:
        raise ValueError('Usuario o contraseña incorrectos')

    usuario_autenticado = authenticate(request, username=usuario.username, password=password)
    if usuario_autenticado is None:
        raise ValueError('Usuario o contraseña incorrectos')

    return generar_jwt(usuario_autenticado)


def enviar_magic_link(email, enlace):
    asunto = 'Tu acceso seguro a EduNúñez'
    texto = f'Usa este enlace para iniciar sesión en EduNúñez: {enlace}'
    html = (
        '<p>Usa este enlace para iniciar sesión en EduNúñez:</p>'
        f'<p><a href="{escape(enlace)}">{escape(enlace)}</a></p>'
    )
    mensaje = EmailMultiAlternatives(
        subject=asunto,
        body=texto,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@edununez.local'),
        to=[email],
    )
    mensaje.attach_alternative(html, 'text/html')
    mensaje.send(fail_silently=False)


def crear_magic_link(email):
    if not email:
        raise ValueError('El email es obligatorio')

    try:
        usuario = User.objects.get(email__iexact=email.strip())
    except User.DoesNotExist:
        raise ValueError('Email no registrado')

    token_obj = MagicLinkToken.objects.create(user=usuario)
    enlace = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').rstrip('/')}/verify?token={token_obj.token}"
    enviar_magic_link(usuario.email, enlace)
    return {'mensaje': 'Magic link enviado. Revisa tu correo.'}


def verificar_magic_link(token):
    if not token:
        raise ValueError('Token no enviado')

    try:
        token_obj = MagicLinkToken.objects.select_related('user').get(token=token)
    except (ObjectDoesNotExist, ValueError):
        raise ValueError('Token inválido')

    if token_obj.used:
        raise ValueError('El token ya fue usado')

    if token_obj.created_at + timedelta(minutes=15) < timezone.now():
        raise ValueError('Token expirado')

    token_obj.used = True
    token_obj.save(update_fields=['used'])
    access = generar_jwt(token_obj.user)
    return {
        'access': access,
        'usuario_id': token_obj.user.id,
        'email': token_obj.user.email,
        'username': token_obj.user.username,
        'nombre_completo': token_obj.user.nombre_completo,
        'rol': token_obj.user.rol,
    }
