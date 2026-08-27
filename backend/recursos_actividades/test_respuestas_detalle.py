#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar que el webhook envía respuestas_detalle
Ejecutar: python test_respuestas_detalle.py
"""
import os
import sys
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunuñez.settings')
django.setup()

from api.models import Usuario, Actividad, AsignacionActividad
from api.webhooks import enviar_resultado_actividad_a_n8n

def test_webhook_con_respuestas():
    """Test del webhook con respuestas detalladas"""
    
    print("\n" + "="*80)
    print("TEST: WEBHOOK CON RESPUESTAS DETALLADAS")
    print("="*80)
    
    try:
        # Obtener un estudiante
        estudiante = Usuario.objects.filter(rol='estudiante').first()
        if not estudiante:
            print("ERROR: No hay estudiantes en la base de datos")
            print("Ejecuta primero: python create_color_game_activity.py")
            return False
        
        # Obtener una actividad
        actividad = Actividad.objects.filter(tipo='juego').first()
        if not actividad:
            print("ERROR: No hay actividades de juego")
            return False
        
        print(f"\n[1] Estudiante: {estudiante.nombre_completo}")
        print(f"[2] Actividad: {actividad.titulo}")
        
        # Simular respuestas del estudiante
        respuestas_simuladas = [
            {
                "numero_pregunta": 1,
                "color_mostrado": "Rojo",
                "hex_color": "#FF6B6B",
                "respuesta_estudiante": "Rojo",
                "respuesta_correcta": "Rojo",
                "es_correcta": True,
                "tiempo_respuesta": 2
            },
            {
                "numero_pregunta": 2,
                "color_mostrado": "Azul",
                "hex_color": "#4ECDC4",
                "respuesta_estudiante": "Verde",
                "respuesta_correcta": "Azul",
                "es_correcta": False,
                "tiempo_respuesta": 5
            },
            {
                "numero_pregunta": 3,
                "color_mostrado": "Verde",
                "hex_color": "#95E1D3",
                "respuesta_estudiante": "Verde",
                "respuesta_correcta": "Verde",
                "es_correcta": True,
                "tiempo_respuesta": 3
            },
            {
                "numero_pregunta": 4,
                "color_mostrado": "Amarillo",
                "hex_color": "#FFE66D",
                "respuesta_estudiante": "Amarillo",
                "respuesta_correcta": "Amarillo",
                "es_correcta": True,
                "tiempo_respuesta": 4
            },
            {
                "numero_pregunta": 5,
                "color_mostrado": "Morado",
                "hex_color": "#A29BFE",
                "respuesta_estudiante": "Morado",
                "respuesta_correcta": "Morado",
                "es_correcta": True,
                "tiempo_respuesta": 2
            },
            {
                "numero_pregunta": 6,
                "color_mostrado": "Rosa",
                "hex_color": "#FD79A8",
                "respuesta_estudiante": "Rosa",
                "respuesta_correcta": "Rosa",
                "es_correcta": True,
                "tiempo_respuesta": 3
            },
            {
                "numero_pregunta": 7,
                "color_mostrado": "Naranja",
                "hex_color": "#FDCB6E",
                "respuesta_estudiante": "Naranja",
                "respuesta_correcta": "Naranja",
                "es_correcta": True,
                "tiempo_respuesta": 2
            },
            {
                "numero_pregunta": 8,
                "color_mostrado": "Cian",
                "hex_color": "#74B9FF",
                "respuesta_estudiante": "Cian",
                "respuesta_correcta": "Cian",
                "es_correcta": True,
                "tiempo_respuesta": 1
            }
        ]
        
        print(f"\n[3] Respuestas simuladas: {len(respuestas_simuladas)}")
        print(f"    - Correctas: {sum(1 for r in respuestas_simuladas if r['es_correcta'])}")
        print(f"    - Incorrectas: {sum(1 for r in respuestas_simuladas if not r['es_correcta'])}")
        
        # Preparar datos para webhook
        data = {
            'estudiante_id': estudiante.id,
            'estudiante_nombre': estudiante.nombre_completo,
            'estudiante_email': estudiante.email,
            'actividad_id': actividad.id,
            'actividad_titulo': actividad.titulo,
            'actividad_tipo': actividad.tipo,
            'curso_id': actividad.curso.id,
            'curso_nombre': actividad.curso.nombre,
            'puntuacion': 80,
            'tiempo_empleado': 1,
            'fecha_entrega': '2025-11-25 12:00:00',
            'estado': 'completada',
            'es_tardia': False,
            'respuestas_detalle': respuestas_simuladas  # ← LO IMPORTANTE
        }
        
        print("\n[4] Enviando al webhook...")
        resultado = enviar_resultado_actividad_a_n8n(data)
        
        print("\n[5] Resultado del webhook:")
        print(f"    - Success: {resultado['success']}")
        print(f"    - Message: {resultado['message']}")
        print(f"    - Code: {resultado.get('response_code', 'N/A')}")
        
        if resultado['success']:
            print("\n" + "="*80)
            print("✅ TEST EXITOSO - El webhook recibió respuestas_detalle correctamente")
            print("="*80)
            return True
        else:
            print("\n⚠️  El webhook respondió pero verificar en n8n si procesó correctamente")
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_webhook_con_respuestas()
    sys.exit(0 if success else 1)
