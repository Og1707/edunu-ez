# -*- coding: utf-8 -*-
"""
Script de prueba para la integración con n8n
Prueba el envío de datos al webhook de n8n
"""

import os
import sys
import io
import django
from django.conf import settings

# Configurar stdout para UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunuñez.settings')
django.setup()

from api.webhooks import enviar_resultado_actividad_a_n8n
from datetime import datetime, timedelta
import json

def test_webhook_envio():
    """Prueba 1: Enviar un resultado básico al webhook"""
    print("\n" + "="*60)
    print("TEST 1: Envío Básico de Resultado")
    print("="*60 + "\n")
    
    test_data = {
        'estudiante_id': 1,
        'estudiante_nombre': 'Juan Pérez López',
        'estudiante_email': 'juan@example.com',
        'actividad_id': 5,
        'actividad_titulo': 'Reconocimiento de Colores',
        'actividad_tipo': 'quiz_ciencias',
        'curso_id': 2,
        'curso_nombre': 'Ciencias Naturales 5°',
        'puntuacion': 85,
        'tiempo_empleado': 8,
        'fecha_entrega': datetime.now(),
        'estado': 'completada',
        'es_tardia': False
    }
    
    print("Enviando datos al webhook...")
    print(f"Estudiante: {test_data['estudiante_nombre']}")
    print(f"Actividad: {test_data['actividad_titulo']}")
    print(f"Puntuacion: {test_data['puntuacion']}/100")
    print(f"Tiempo: {test_data['tiempo_empleado']} minutos")
    print()
    
    result = enviar_resultado_actividad_a_n8n(test_data)
    
    print(f"Exito: {result['success']}")
    print(f"Mensaje: {result['message']}")
    print(f"Codigo HTTP: {result['response_code']}")
    if 'response_body' in result:
        print(f"📋 Respuesta: {result['response_body'][:200]}")
    
    return result['success']


def test_webhook_puntuacion_baja():
    """Prueba 2: Resultado con puntuación baja"""
    print("\n" + "="*60)
    print("TEST 2: Resultado con Puntuación Baja")
    print("="*60 + "\n")
    
    test_data = {
        'estudiante_id': 2,
        'estudiante_nombre': 'María González Martínez',
        'estudiante_email': 'maria@example.com',
        'actividad_id': 5,
        'actividad_titulo': 'Reconocimiento de Colores',
        'actividad_tipo': 'quiz_ciencias',
        'curso_id': 2,
        'curso_nombre': 'Ciencias Naturales 5°',
        'puntuacion': 45,
        'tiempo_empleado': 15,
        'fecha_entrega': datetime.now(),
        'estado': 'completada',
        'es_tardia': False
    }
    
    print("Enviando datos de resultado bajo...")
    print(f"Estudiante: {test_data['estudiante_nombre']}")
    print(f"Puntuacion: {test_data['puntuacion']}/100 (BAJA)")
    
    result = enviar_resultado_actividad_a_n8n(test_data)
    
    print(f"Exito: {result['success']}")
    print(f"Mensaje: {result['message']}")
    
    return result['success']


def test_webhook_entrega_tardia():
    """Prueba 3: Resultado con entrega tardía"""
    print("\n" + "="*60)
    print("TEST 3: Resultado con Entrega Tardía")
    print("="*60 + "\n")
    
    test_data = {
        'estudiante_id': 3,
        'estudiante_nombre': 'Carlos Rodríguez Silva',
        'estudiante_email': 'carlos@example.com',
        'actividad_id': 5,
        'actividad_titulo': 'Reconocimiento de Colores',
        'actividad_tipo': 'quiz_ciencias',
        'curso_id': 2,
        'curso_nombre': 'Ciencias Naturales 5°',
        'puntuacion': 72,
        'tiempo_empleado': 20,
        'fecha_entrega': datetime.now(),
        'estado': 'completada',
        'es_tardia': True  # ← TARDÍA
    }
    
    print("Enviando datos de entrega tardia...")
    print(f"Estudiante: {test_data['estudiante_nombre']}")
    print(f"Puntuacion: {test_data['puntuacion']}/100")
    print(f"Estado: ENTREGA TARDIA")
    
    result = enviar_resultado_actividad_a_n8n(test_data)
    
    print(f"Exito: {result['success']}")
    print(f"Mensaje: {result['message']}")
    
    return result['success']


def test_webhook_puntuacion_perfecta():
    """Prueba 4: Resultado con puntuación perfecta"""
    print("\n" + "="*60)
    print("TEST 4: Resultado con Puntuación Perfecta")
    print("="*60 + "\n")
    
    test_data = {
        'estudiante_id': 4,
        'estudiante_nombre': 'Ana Martínez López',
        'estudiante_email': 'ana@example.com',
        'actividad_id': 5,
        'actividad_titulo': 'Reconocimiento de Colores',
        'actividad_tipo': 'quiz_ciencias',
        'curso_id': 2,
        'curso_nombre': 'Ciencias Naturales 5°',
        'puntuacion': 100,
        'tiempo_empleado': 5,
        'fecha_entrega': datetime.now(),
        'estado': 'completada',
        'es_tardia': False
    }
    
    print("Enviando datos de resultado perfecto...")
    print(f"Estudiante: {test_data['estudiante_nombre']}")
    print(f"Puntuacion: {test_data['puntuacion']}/100 PERFECTA")
    print(f"Tiempo: {test_data['tiempo_empleado']} minutos (Muy rapido!)")
    
    result = enviar_resultado_actividad_a_n8n(test_data)
    
    print(f"Exito: {result['success']}")
    print(f"Mensaje: {result['message']}")
    
    return result['success']


def test_webhook_error_conexion():
    """Prueba 5: Verificar manejo de errores de conexión"""
    print("\n" + "="*60)
    print("TEST 5: Manejo de Errores de Conexión")
    print("="*60 + "\n")
    
    # Simulamos un webhook con URL inválida temporalmente
    from api.webhooks import WEBHOOKS_CONFIG
    
    original_url = WEBHOOKS_CONFIG['n8n_alumnos']['url']
    
    try:
        WEBHOOKS_CONFIG['n8n_alumnos']['url'] = 'http://localhost:5678/webhook/Alumnos_settings'
        
        test_data = {
            'estudiante_id': 5,
            'estudiante_nombre': 'Test Error',
            'estudiante_email': 'error@test.com',
            'actividad_id': 1,
            'actividad_titulo': 'Error Test',
            'actividad_tipo': 'quiz_ciencias',
            'curso_id': 1,
            'curso_nombre': 'Test',
            'puntuacion': 50,
            'tiempo_empleado': 10,
            'fecha_entrega': datetime.now(),
            'estado': 'completada',
            'es_tardia': False
        }
        
        print("Enviando a URL invalida para probar manejo de errores...")
        result = enviar_resultado_actividad_a_n8n(test_data)
        
        print(f"Exito: {result['success']} (Se espera False)")
        print(f"Mensaje: {result['message']}")
        print(f"Codigo: {result['response_code']}")
        
        # Validar que el error fue manejado correctamente
        return result['success'] == False  # Retorna True si manejó el error correctamente
        
    finally:
        # Restaurar URL original
        WEBHOOKS_CONFIG['n8n_alumnos']['url'] = original_url


def test_webhook_multiples():
    """Prueba 6: Enviar múltiples resultados"""
    print("\n" + "="*60)
    print("TEST 6: Envío de Múltiples Resultados")
    print("="*60 + "\n")
    
    estudiantes = [
        ('Pedro García', 'pedro@example.com', 78),
        ('Laura Fernández', 'laura@example.com', 92),
        ('Diego López', 'diego@example.com', 65),
        ('Sofia Rodríguez', 'sofia@example.com', 88),
        ('Miguel Torres', 'miguel@example.com', 55),
    ]
    
    resultados = []
    
    for idx, (nombre, email, puntuacion) in enumerate(estudiantes, start=1):
        test_data = {
            'estudiante_id': idx + 10,
            'estudiante_nombre': nombre,
            'estudiante_email': email,
            'actividad_id': 5,
            'actividad_titulo': 'Reconocimiento de Colores',
            'actividad_tipo': 'quiz_ciencias',
            'curso_id': 2,
            'curso_nombre': 'Ciencias Naturales 5°',
            'puntuacion': puntuacion,
            'tiempo_empleado': 7 + idx,
            'fecha_entrega': datetime.now(),
            'estado': 'completada',
            'es_tardia': False
        }
        
        print(f"\n  [{idx}/{len(estudiantes)}] Enviando para {nombre}...")
        result = enviar_resultado_actividad_a_n8n(test_data)
        
        status = "OK" if result['success'] else "FALLO"
        print(f"      [{status}] Puntuacion: {puntuacion}/100")
        
        resultados.append(result['success'])
    
    total_exito = sum(resultados)
    print(f"\nResumen: {total_exito}/{len(resultados)} envios exitosos")
    
    return total_exito == len(resultados)


def mostrar_resumen():
    """Muestra resumen de configuracion"""
    print("\n" + "="*60)
    print("CONFIGURACION DE WEBHOOK")
    print("="*60 + "\n")
    
    from api.webhooks import WEBHOOKS_CONFIG
    
    config = WEBHOOKS_CONFIG['n8n_alumnos']
    
    print(f"URL: {config['url']}")
    print(f"Timeout: {config['timeout']} segundos")
    print(f"Reintentos: {config['retry_attempts']}")
    print(f"Habilitado: {'Si' if config['enabled'] else 'No'}")


def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("Tests de Integracion con n8n")
    print("Webhooks para Actividades Completadas")
    print("="*60)
    
    mostrar_resumen()
    
    resultados = {
        'Test 1 - Envio Basico': test_webhook_envio(),
        'Test 2 - Puntuacion Baja': test_webhook_puntuacion_baja(),
        'Test 3 - Entrega Tardia': test_webhook_entrega_tardia(),
        'Test 4 - Puntuacion Perfecta': test_webhook_puntuacion_perfecta(),
        'Test 5 - Manejo de Errores': test_webhook_error_conexion(),
        'Test 6 - Multiples Resultados': test_webhook_multiples(),
    }
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN FINAL DE TESTS")
    print("="*60 + "\n")
    
    total_tests = len(resultados)
    tests_exitosos = sum(1 for v in resultados.values() if v)
    
    for test_name, resultado in resultados.items():
        status = "OK" if resultado else "FALLO"
        print(f"  [{status}]: {test_name}")
    
    print(f"\nTotal: {tests_exitosos}/{total_tests} tests exitosos")
    
    if tests_exitosos == total_tests:
        print("\nExito: TODOS LOS TESTS PASARON! El webhook esta funcionando.")
    else:
        print(f"\nAdvertencia: {total_tests - tests_exitosos} test(s) fallaron. Revisa la configuracion.")
    
    print("\n" + "="*60 + "\n")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nError fatal: {str(e)}")
        import traceback
        traceback.print_exc()
