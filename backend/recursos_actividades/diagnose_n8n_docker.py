#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnostico para n8n en Docker + Django
Verifica toda la conectividad y configuracion
"""

import os
import sys
import io
import subprocess
import requests
import json
from datetime import datetime

# Configurar stdout para UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    """Imprime un header formateado"""
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_ok(text):
    """Imprime mensaje OK"""
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {text}")

def print_fail(text):
    """Imprime mensaje FALLO"""
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {text}")

def print_warning(text):
    """Imprime mensaje WARNING"""
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET} {text}")

def print_info(text):
    """Imprime mensaje INFO"""
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {text}")

def check_docker_installed():
    """Verifica si Docker está instalado"""
    print_header("1. VERIFICAR DOCKER INSTALADO")
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_ok(f"Docker instalado: {result.stdout.strip()}")
            return True
        else:
            print_fail("Docker no está instalado o no está en PATH")
            return False
    except FileNotFoundError:
        print_fail("Docker no encontrado. Instala Docker Desktop")
        return False

def check_n8n_running():
    """Verifica si n8n está corriendo en Docker"""
    print_header("2. VERIFICAR n8n EN DOCKER")
    
    try:
        result = subprocess.run(['docker', 'ps', '--format', 'json'], capture_output=True, text=True)
        if result.returncode == 0:
            containers = result.stdout.strip()
            if 'n8n' in containers:
                print_ok("n8n está corriendo en Docker")
                
                # Obtener ID del container
                result = subprocess.run(['docker', 'ps', '--filter', 'name=n8n', '--format', '{{.ID}}'], 
                                      capture_output=True, text=True)
                container_id = result.stdout.strip()
                if container_id:
                    print_info(f"Container ID: {container_id}")
                    return container_id
            else:
                print_fail("n8n no está en docker ps")
                print_info("Iniciando n8n...")
                subprocess.run(['docker', 'run', '-d', '-p', '5678:5678', 'n8n'])
                return None
        else:
            print_fail(f"Error ejecutando docker ps: {result.stderr}")
            return None
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return None

def check_port_mapped(container_id):
    """Verifica si el puerto está mapeado correctamente"""
    print_header("3. VERIFICAR PUERTO MAPEADO")
    
    try:
        result = subprocess.run(['docker', 'port', container_id], capture_output=True, text=True)
        output = result.stdout.strip()
        
        if '5678' in output:
            print_ok(f"Puerto mapeado correctamente:\n{output}")
            
            # Extraer el puerto del host
            if '5678/tcp' in output:
                host_port = output.split('->')[0].strip().split(':')[-1]
                print_info(f"Puerto en host: {host_port}")
                return host_port
        else:
            print_fail("Puerto 5678 no está mapeado")
            return None
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return None

def check_browser_access(port):
    """Verifica si puedes acceder a n8n desde el navegador (simulado)"""
    print_header("4. VERIFICAR ACCESO DESDE NAVEGADOR")
    
    url = f'http://localhost:{port}'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print_ok(f"Acceso exitoso a {url}")
            return True
        else:
            print_warning(f"Status {response.status_code} (esperado 200)")
            return False
    except requests.exceptions.ConnectionError:
        print_fail(f"No se puede conectar a {url}")
        print_warning("Posible causa: Firewall de Windows")
        return False
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return False

def check_django_access(port):
    """Verifica si Django puede conectar a n8n"""
    print_header("5. VERIFICAR ACCESO DESDE DJANGO")
    
    url = f'http://localhost:{port}'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print_ok(f"Django puede conectar a {url}")
            return True
        else:
            print_warning(f"Status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError as e:
        print_fail(f"Django NO puede conectar a {url}")
        print_warning(f"Error: {str(e)}")
        return False
    except Exception as e:
        print_fail(f"Error: {str(e)}")
        return False

def check_webhook_exists(port):
    """Verifica si el webhook existe en n8n"""
    print_header("6. VERIFICAR WEBHOOK EN n8n")
    
    url = f'http://localhost:{port}/webhook/Alumnos_settings'
    try:
        # Un webhook POST sin datos debe retornar algo (depende del flujo)
        response = requests.post(url, json={'test': True}, timeout=5)
        
        if response.status_code in [200, 201, 202, 204, 400]:
            print_ok(f"Webhook responde con status {response.status_code}")
            return True
        elif response.status_code == 404:
            print_fail(f"Webhook no encontrado (404)")
            print_warning("Verifica que el webhook existe en n8n con la ruta correcta")
            return False
        else:
            print_warning(f"Webhook respondio con status {response.status_code}")
            return True
    except Exception as e:
        print_fail(f"Error al acceder al webhook: {str(e)}")
        return False

def check_webhook_config():
    """Verifica la configuración en webhooks.py"""
    print_header("7. VERIFICAR CONFIGURACION EN webhooks.py")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Cargar settings de Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunuñez.settings')
        
        import django
        django.setup()
        
        from api.webhooks import WEBHOOKS_CONFIG
        
        config = WEBHOOKS_CONFIG.get('n8n_alumnos', {})
        
        print_info("Configuración actual:")
        print(f"  URL: {config.get('url')}")
        print(f"  Timeout: {config.get('timeout')}s")
        print(f"  Reintentos: {config.get('retry_attempts')}")
        print(f"  Habilitado: {config.get('enabled')}")
        
        if config.get('enabled'):
            print_ok("Webhooks habilitado")
        else:
            print_fail("Webhooks deshabilitado")
        
        return config
    except Exception as e:
        print_fail(f"Error al cargar configuración: {str(e)}")
        return None

def run_webhook_test():
    """Ejecuta un test de webhook"""
    print_header("8. EJECUTAR TEST DE WEBHOOK")
    
    try:
        from api.webhooks import enviar_resultado_actividad_a_n8n
        from datetime import datetime
        
        test_data = {
            'estudiante_id': 1,
            'estudiante_nombre': 'Test Usuario',
            'estudiante_email': 'test@example.com',
            'actividad_id': 1,
            'actividad_titulo': 'Test Actividad',
            'actividad_tipo': 'test',
            'curso_id': 1,
            'curso_nombre': 'Test Curso',
            'puntuacion': 85,
            'tiempo_empleado': 5,
            'fecha_entrega': datetime.now(),
            'estado': 'completada',
            'es_tardia': False
        }
        
        print_info("Enviando test de webhook...")
        result = enviar_resultado_actividad_a_n8n(test_data)
        
        if result['success']:
            print_ok(f"Webhook enviado exitosamente (Status {result['response_code']})")
            return True
        else:
            print_fail(f"Webhook falló: {result['message']}")
            return False
    except Exception as e:
        print_fail(f"Error en test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(checks):
    """Imprime resumen de verificaciones"""
    print_header("RESUMEN DIAGNOSTICO")
    
    total = len(checks)
    passed = sum(1 for v in checks.values() if v)
    
    for check_name, result in checks.items():
        status = "OK" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {check_name}: {status}")
    
    print(f"\n{passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print_ok("DIAGNOSTICO COMPLETO: Todo funciona correctamente!")
        return True
    else:
        print_fail(f"DIAGNOSTICO INCOMPLETO: {total - passed} verificaciones fallaron")
        return False

def main():
    """Función principal"""
    print(f"\n{Colors.BLUE}Iniciando diagnostico de n8n + Django{Colors.RESET}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    checks = {}
    
    # Check 1: Docker instalado
    docker_ok = check_docker_installed()
    checks['Docker instalado'] = docker_ok
    
    if not docker_ok:
        print_fail("No puedo continuar sin Docker")
        return False
    
    # Check 2: n8n corriendo
    container_id = check_n8n_running()
    checks['n8n en Docker'] = container_id is not None
    
    if not container_id:
        print_warning("n8n no fue encontrado. Intenta iniciarlo manualmente")
        return False
    
    # Check 3: Puerto mapeado
    port = check_port_mapped(container_id)
    checks['Puerto mapeado'] = port is not None
    
    if not port:
        print_warning("No se pudo detectar puerto. Usando default 5678")
        port = '5678'
    
    # Check 4: Acceso desde navegador
    browser_ok = check_browser_access(port)
    checks['Acceso navegador'] = browser_ok
    
    # Check 5: Acceso desde Django
    django_ok = check_django_access(port)
    checks['Acceso Django'] = django_ok
    
    # Check 6: Webhook existe
    webhook_ok = check_webhook_exists(port)
    checks['Webhook existe'] = webhook_ok
    
    # Check 7: Configuración
    config_ok = check_webhook_config()
    checks['Configuracion OK'] = config_ok is not None
    
    # Check 8: Test
    if django_ok:
        test_ok = run_webhook_test()
        checks['Test webhook'] = test_ok
    
    # Resumen
    success = print_summary(checks)
    
    print("\n" + "="*70)
    if success:
        print("SIGUIENTE PASO: Ejecuta 'python edunuñez/test_n8n_webhook.py'")
    else:
        print("SIGUIENTE PASO: Revisa los errores arriba y consulta N8N_DOCKER_DIAGNOSTICO.md")
    print("="*70 + "\n")
    
    return success

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print_fail(f"Error fatal: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
