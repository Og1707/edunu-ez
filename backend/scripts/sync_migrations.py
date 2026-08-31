import os
import datetime
import psycopg
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / '.env')
load_dotenv(BASE_DIR / '.env')

db_url = os.environ.get('DATABASE_URL')
if db_url:
    conn = psycopg.connect(db_url)
else:
    conn = psycopg.connect(
        dbname=os.environ.get('DB_NAME', 'edununez'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        host=os.environ.get('DB_HOST', '127.0.0.1'),
        port=os.environ.get('DB_PORT', '5432')
    )
cur = conn.cursor()
now = datetime.datetime.now(datetime.timezone.utc)
modular_migrations = [
    ('usuarios', '0001_initial'),
    ('cursos', '0001_initial'),
    ('cursos', '0002_initial'),
    ('actividades', '0001_initial'),
    ('actividades', '0002_initial'),
    ('ciencias', '0001_initial'),
    ('ciencias', '0002_initial'),
    ('juegos', '0001_initial'),
    ('juegos', '0002_initial'),
]
for app, name in modular_migrations:
    cur.execute('INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s);', (app, name, now))
cur.execute("DELETE FROM django_migrations WHERE app = 'api';")
conn.commit()
print('Migraciones actualizadas con exito!')
