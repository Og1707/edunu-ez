from rest_framework import serializers
from .models import usuario
from django.contrib.auth.hashers import make_password, check_password

class RegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = usuario
        fields = ['nombre', 'email', 'password', 'roles']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        user = usuario(
            nombre=validated_data['nombre'],
            email=validated_data['email'],
            roles=validated_data['roles'],
        )
        user.set_password(validated_data['password'])  # Usa set_password aquí
        user.save()
        return user

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = usuario
        fields = ['email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validar(self, data):
        try:
            user = usuario.objects.get(email=data['email'])
            if not check_password(data['password'], user.password):
                raise serializers.ValidationError("Contraseña incorrecta")
        except usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        
        return data

class OlvideContrasenaSerializer(serializers.Serializer):
    email = serializers.EmailField()