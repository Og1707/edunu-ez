from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import *
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token
from django.utils.encoding import force_bytes
from django.conf import settings


User = get_user_model()

class RegistroView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegistroSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'Usuario registrado con éxito'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        return Response({'message': 'Bienvenido a la API de registro de usuarios'}, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

class OlvideContrasenaView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OlvideContrasenaSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = usuario.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = f"http://localhost:8000/reset_password/{uid}/{token}/"
                send_mail(
                    'Restablece tu contraseña',
                    f'Usa este enlace para restablecer tu contraseña: {reset_url}',
                    'no-reply@tusitio.com',
                    [email],
                    fail_silently=False,
                )
                return Response({'message': 'Correo de recuperación enviado'}, status=status.HTTP_200_OK)
            except usuario.DoesNotExist:
                return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)