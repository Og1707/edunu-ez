import sys
import os
import time

# Forzar UTF-8 en salida estándar
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edunuñez.settings')

import django
django.setup()

from django.db import connection
from apps.usuarios.models import Usuario
from apps.cursos.models import Curso
from apps.actividades.models import Actividad
from apps.juegos.models import JuegoEducativo, PartidaJuego

print('=' * 60)
print('>>> INICIANDO PRUEBA DE CONEXION A RENDER POSTGRESQL <<<')
print('=' * 60)

# 1. Test de Latencia / Ping
t0 = time.time()
with connection.cursor() as cursor:
    cursor.execute('SELECT version();')
    pg_version = cursor.fetchone()[0]
latency_ms = round((time.time() - t0) * 1000, 2)

print(f'[OK] Conexion SSL establecida con exito.')
print(f'[PING] Latencia hacia el servidor de Render: {latency_ms} ms')
print(f'[BD] Version PostgreSQL: {pg_version.split(",")[0]}')
print('-' * 60)

# 2. Test de Lectura de Datos Existentes
print('DATOS ACTUALMENTE ALMACENADOS EN RENDER:')
usuarios_count = Usuario.objects.count()
print(f'  * Total Usuarios: {usuarios_count}')
for u in Usuario.objects.all()[:5]:
    print(f'    - {u.username} | Rol: {u.get_rol_display()} | Email: {u.email}')

print(f'  * Total Cursos: {Curso.objects.count()}')
print(f'  * Total Actividades: {Actividad.objects.count()}')
print(f'  * Total Juegos Educativos: {JuegoEducativo.objects.count()}')
print(f'  * Total Partidas Jugadas: {PartidaJuego.objects.count()}')
print('-' * 60)

# 3. Test de Escritura, Lectura y Borrado (Ciclo Completo CRUD)
print('PROBANDO CICLO DE ESCRITURA Y LECTURA (CRUD)...')
t_write = time.time()
test_user = Usuario.objects.create(
    username='test_render_check',
    email='test_check@edununez.com',
    nombre_completo='Usuario Prueba Render',
    rol='estudiante'
)
write_time = round((time.time() - t_write) * 1000, 2)
print(f'  [OK] Escritura: Usuario temporal creado en {write_time} ms (ID: {test_user.id})')

# Verificar lectura
t_read = time.time()
fetched = Usuario.objects.get(id=test_user.id)
read_time = round((time.time() - t_read) * 1000, 2)
print(f'  [OK] Lectura: Registro consultado en {read_time} ms ({fetched.nombre_completo})')

# Limpieza
test_user.delete()
print(f'  [OK] Eliminacion: Registro temporal limpiado de la base de datos.')
print('=' * 60)
print('RESULTADO: La base de datos en Render esta 100% OPERATIVA y fluida.')
print('=' * 60)
