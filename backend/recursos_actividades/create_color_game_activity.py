#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para crear una actividad de juego de colores y asignarla a estudiantes
Ejecutar desde: python create_color_game_activity.py
"""
import os
import sys
import django

# Configurar Django ANTES de importar modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunuñez.settings')
django.setup()

from api.models import Usuario, Curso, Actividad, AsignacionActividad, EstudianteCurso
from django.utils import timezone
from datetime import timedelta

def create_color_game_activity():
    """Crea una actividad de juego de colores para pruebas"""
    
    print("=" * 60)
    print("🎨 CREAR ACTIVIDAD DE JUEGO DE COLORES")
    print("=" * 60)
    
    # 1. Buscar o crear profesor
    print("\n1️⃣  Buscando profesor...")
    try:
        profesor = Usuario.objects.get(rol='profesor')
        print(f"   ✓ Profesor encontrado: {profesor.nombre_completo}")
    except Usuario.DoesNotExist:
        print("   ⚠️  No hay profesores disponibles")
        print("   Creando profesor de prueba...")
        profesor = Usuario.objects.create_user(
            username='profesor_juegos',
            email='profesor@juegos.com',
            password='test123456',
            nombre_completo='Profesor de Juegos',
            rol='profesor'
        )
        print(f"   ✓ Profesor creado: {profesor.nombre_completo}")
    
    # 2. Buscar o crear curso
    print("\n2️⃣  Buscando curso...")
    try:
        curso = Curso.objects.filter(profesor=profesor).first()
        if not curso:
            raise Curso.DoesNotExist
        print(f"   ✓ Curso encontrado: {curso.nombre}")
    except Curso.DoesNotExist:
        print("   ⚠️  No hay cursos disponibles")
        print("   Creando curso de prueba...")
        curso = Curso.objects.create(
            nombre='Ciencias Naturales - Juegos',
            descripcion='Curso con juegos interactivos educativos',
            profesor=profesor
        )
        print(f"   ✓ Curso creado: {curso.nombre}")
    
    # 3. Buscar o crear estudiantes
    print("\n3️⃣  Buscando estudiantes...")
    estudiantes = Usuario.objects.filter(rol='estudiante')[:5]
    if not estudiantes.exists():
        print("   ⚠️  No hay estudiantes disponibles")
        print("   Creando estudiantes de prueba...")
        estudiantes = []
        for i in range(1, 4):
            estudiante = Usuario.objects.create_user(
                username=f'estudiante{i}',
                email=f'estudiante{i}@test.com',
                password='test123456',
                nombre_completo=f'Estudiante {i}',
                rol='estudiante'
            )
            estudiantes.append(estudiante)
            print(f"   ✓ Estudiante {i} creado")
    else:
        print(f"   ✓ {len(estudiantes)} estudiantes encontrados")
    
    # 4. Inscribir estudiantes en el curso
    print("\n4️⃣  Inscribiendo estudiantes en el curso...")
    for estudiante in estudiantes:
        inscripcion, created = EstudianteCurso.objects.get_or_create(
            estudiante=estudiante,
            curso=curso
        )
        if created:
            print(f"   ✓ {estudiante.nombre_completo} inscrito")
        else:
            print(f"   ℹ️  {estudiante.nombre_completo} ya estaba inscrito")
    
    # 5. Crear actividad del juego
    print("\n5️⃣  Creando actividad de juego de colores...")
    
    actividad, created = Actividad.objects.get_or_create(
        titulo='Juego de Reconocimiento de Colores',
        defaults={
            'descripcion': '''
🎨 **Juego Interactivo: Reconocimiento de Colores**

En este juego educativo, deberás identificar correctamente los nombres de los colores que se muestran en la pantalla.

**¿Cómo funciona?**
1. Se mostrarán 10 rondas de colores
2. Para cada color, deberás seleccionar el nombre correcto entre 4 opciones
3. Tu velocidad y precisión serán registradas por un cronómetro automático
4. La puntuación se basa en el número de aciertos

**Objetivos de aprendizaje:**
- Reconocer y nombrar colores en inglés
- Mejorar la velocidad de reconocimiento visual
- Desarrollar habilidades de atención y concentración

**Tiempo estimado:** 5 minutos

¡A jugar y aprender! 🌈
            '''.strip(),
            'tipo': 'quiz_ciencias',
            'curso': curso,
            'creado_por': profesor,
            'fecha_limite': timezone.now() + timedelta(days=30),
            'estado': 'activa'
        }
    )
    
    if created:
        print(f"   ✓ Actividad creada: {actividad.titulo}")
        print(f"     ID: {actividad.id}")
        print(f"     Tipo: {actividad.tipo}")
        print(f"     Fecha límite: {actividad.fecha_limite}")
    else:
        print(f"   ℹ️  Actividad ya existía: {actividad.titulo}")
    
    # 6. Asignar actividad a estudiantes
    print("\n6️⃣  Asignando actividad a estudiantes...")
    asignaciones_creadas = 0
    asignaciones_existentes = 0
    
    for estudiante in estudiantes:
        asignacion, created = AsignacionActividad.objects.get_or_create(
            actividad=actividad,
            estudiante=estudiante,
            defaults={
                'profesor': profesor,
                'estado': 'asignada'
            }
        )
        
        if created:
            asignaciones_creadas += 1
            print(f"   ✓ Asignación creada para {estudiante.nombre_completo}")
        else:
            asignaciones_existentes += 1
            print(f"   ℹ️  Asignación ya existía para {estudiante.nombre_completo}")
    
    # 7. Resumen
    print("\n" + "=" * 60)
    print("✅ RESUMEN DE LA OPERACIÓN")
    print("=" * 60)
    print(f"Profesor: {profesor.nombre_completo}")
    print(f"Curso: {curso.nombre}")
    print(f"Actividad: {actividad.titulo}")
    print(f"Estudiantes inscritos: {len(estudiantes)}")
    print(f"Nuevas asignaciones: {asignaciones_creadas}")
    print(f"Asignaciones existentes: {asignaciones_existentes}")
    print(f"Total de asignaciones: {asignaciones_creadas + asignaciones_existentes}")
    
    print("\n" + "=" * 60)
    print("🎮 DATOS DE PRUEBA")
    print("=" * 60)
    
    for i, estudiante in enumerate(estudiantes, 1):
        print(f"\nEstudiante {i}:")
        print(f"  Username: {estudiante.username}")
        print(f"  Email: {estudiante.email}")
        print(f"  Contraseña: test123456")
        print(f"  Nombre: {estudiante.nombre_completo}")
    
    print(f"\nProfesor:")
    print(f"  Username: {profesor.username}")
    print(f"  Email: {profesor.email}")
    print(f"  Contraseña: test123456")
    print(f"  Nombre: {profesor.nombre_completo}")
    
    print(f"\nActividad:")
    print(f"  ID: {actividad.id}")
    print(f"  Título: {actividad.titulo}")
    print(f"  Tipo: {actividad.tipo}")
    print(f"  Curso ID: {curso.id}")
    print(f"  Curso: {curso.nombre}")
    
    print("\n" + "=" * 60)
    print("📝 PASOS SIGUIENTES")
    print("=" * 60)
    print("1. Inicia React: npm start")
    print("2. Abre: http://localhost:3000")
    print("3. Inicia sesión como estudiante")
    print("4. Ve a 'Mis Actividades'")
    print("5. Verás 'Juego de Reconocimiento de Colores'")
    print("6. Haz clic en 'Iniciar Actividad'")
    print("7. ¡Juega y diviértete! 🎮")
    print("=" * 60)

if __name__ == '__main__':
    create_color_game_activity()
    print("\n✨ ¡Script completado exitosamente!")
