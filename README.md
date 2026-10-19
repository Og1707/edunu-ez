# EduNúñez

<p align="center">
  <strong>Plataforma educativa para conectar docentes y estudiantes</strong><br>
  Gestión de cursos, actividades y experiencias de aprendizaje desde una sola aplicación.
</p>

<p align="center">
  <img alt="Python 3.11" src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white">
  <img alt="Django 5.2" src="https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white">
  <img alt="React 19" src="https://img.shields.io/badge/React-19-149ECA?logo=react&logoColor=white">
  <img alt="PostgreSQL 16" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white">
  <img alt="Redis 7" src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white">
</p>

---

## 📚 Contenido

- [Acerca del proyecto](#-acerca-del-proyecto)
- [Qué puedes hacer](#-qué-puedes-hacer)
- [Tecnologías](#-tecnologías)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Inicio rápido en local](#-inicio-rápido-en-local)
- [Ejecución con Docker](#-ejecución-con-docker)
- [Configuración](#-configuración)
- [API y comprobaciones](#-api-y-comprobaciones)
- [Pruebas](#-pruebas)
- [Estructura del repositorio](#-estructura-del-repositorio)
- [Documentación adicional](#-documentación-adicional)

## 🎓 Acerca del proyecto

EduNúñez es una plataforma educativa desarrollada como proyecto de grado. Ofrece herramientas para que administradores y docentes organicen cursos y actividades, y para que los estudiantes accedan a sus actividades y consulten su progreso.

La aplicación está construida como una SPA en React conectada a una API REST en Django. La API aplica permisos según el rol del usuario y ofrece documentación interactiva OpenAPI.

## ✨ Qué puedes hacer

| Área | Funcionalidades |
|---|---|
| 👥 Usuarios | Registro, autenticación, gestión de usuarios y acceso según rol. |
| 🏫 Cursos | Crear cursos, administrar asignaturas y asociar docentes y estudiantes. |
| 📝 Actividades | Crear actividades de texto y multimedia, asignarlas a cursos y registrar entregas. |
| 📊 Seguimiento | Consultar resúmenes y progreso de estudiantes. |
| 🎮 Aprendizaje lúdico | Explorar juegos educativos y registrar partidas. |
| 🌿 Ciencias | Consultar temas y contenidos de Wikipedia para apoyar actividades de ciencias. |
| 🔗 Integraciones | Almacenar multimedia con Cloudinary y enviar eventos a n8n mediante webhooks. |

## 🧰 Tecnologías

| Componente | Tecnologías principales |
|---|---|
| Frontend | React 19, React Router, Axios, Tailwind CSS |
| Backend | Python 3.11, Django 5.2, Django REST Framework, SimpleJWT |
| Datos y caché | PostgreSQL 16, Redis 7 |
| Operación | Docker Compose, Gunicorn, Sentry opcional |

## 🏗️ Arquitectura

```mermaid
flowchart LR
    U[Docente / estudiante / administrador] --> FE[Frontend React]
    FE -->|HTTP / JSON| API[API REST Django]
    API --> DB[(PostgreSQL)]
    API --> R[(Redis)]
    API -. archivos multimedia .-> C[Cloudinary]
    API -. eventos .-> N[n8n]
```

## ✅ Requisitos

- Python 3.11.
- Node.js y npm (se recomienda Node.js 18 o superior para el frontend actual).
- PostgreSQL 16 y Redis 7 para desarrollo local, o Docker Desktop con Docker Compose.

## 🚀 Inicio rápido en local

### 1. Configurar variables y servicios

Desde la raíz del repositorio, crea tu archivo de entorno:

```powershell
Copy-Item .env.example .env
```

El backend usa PostgreSQL por defecto. Puedes iniciar PostgreSQL y Redis con Docker Compose:

```powershell
docker compose up -d db redis
```

Si utilizas instalaciones locales de PostgreSQL o Redis, asegúrate de que coincidan con los valores de `.env`.

### 2. Instalar e iniciar el backend

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

El backend queda disponible en `http://127.0.0.1:8000`.

> En macOS o Linux, crea el entorno con `python3.11 -m venv .venv` y actívalo con `source .venv/bin/activate`.

### 3. Instalar e iniciar el frontend

En otra terminal, desde la raíz:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm start
```

El frontend queda disponible en `http://localhost:3000`. La variable `REACT_APP_API_URL` apunta por defecto a `http://127.0.0.1:8000`.

### 4. Crear un usuario administrador

En una terminal con el entorno virtual del backend activado:

```powershell
cd backend
python manage.py createsuperuser
```

## 🐳 Ejecución con Docker

El Compose del proyecto levanta PostgreSQL, Redis y el backend Django. El frontend se ejecuta por separado con npm, siguiendo los pasos anteriores.

El backend de Compose usa la configuración de producción. Antes de iniciarlo, rellena `DJANGO_SECRET_KEY` y `N8N_WEBHOOK_SECRET` en `.env` con valores aleatorios; ambos campos vienen vacíos en el archivo de ejemplo.

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose exec backend python manage.py migrate
docker compose logs -f backend
```

La API queda en `http://localhost:8000`. Para detener los servicios:

```powershell
docker compose down
```

Los datos de PostgreSQL y Redis se guardan en volúmenes Docker. `docker compose down -v` también elimina esos datos.

## ⚙️ Configuración

Las variables principales se documentan en [`.env.example`](.env.example). El backend busca `.env` primero dentro de `backend/` y luego en la raíz.

| Variable | Uso |
|---|---|
| `DJANGO_SETTINGS_MODULE` | Configuración activa; para desarrollo local usa `edunuñez.settings.development`. |
| `DJANGO_SECRET_KEY` | Clave secreta de Django; define una clave segura en despliegues. |
| `DATABASE_URL` | Conexión PostgreSQL, por ejemplo `postgres://postgres:postgres@localhost:5432/edununez`. |
| `DJANGO_REDIS_URL` | Conexión Redis para caché. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Orígenes permitidos para el frontend. |
| `FRONTEND_URL` | URL usada para generar enlaces de autenticación por correo. |
| `CLOUDINARY_*` | Credenciales de almacenamiento multimedia; necesarias para esa integración. |
| `N8N_WEBHOOK_*` | URL, activación y autenticación de webhooks n8n. |
| `SENTRY_DSN` | DSN opcional para monitoreo de errores. |

No compartas el archivo `.env` ni incluyas secretos en el repositorio. El backend de correo de desarrollo imprime los mensajes en la consola; configura SMTP si necesitas entrega real.

## 📡 API y comprobaciones

Con el backend iniciado:

| Recurso | URL |
|---|---|
| Estado del servicio | [`/api/health/`](http://127.0.0.1:8000/api/health/) |
| Swagger UI | [`/api/docs/`](http://127.0.0.1:8000/api/docs/) |
| ReDoc | [`/api/redoc/`](http://127.0.0.1:8000/api/redoc/) |
| Esquema OpenAPI | [`/api/schema/`](http://127.0.0.1:8000/api/schema/) |
| Panel de administración | [`/admin/`](http://127.0.0.1:8000/admin/) |

La API agrupa endpoints de autenticación, usuarios, cursos, actividades, dashboards, juegos, ciencias, plantillas y webhooks. Revisa Swagger para ver operaciones, parámetros y respuestas disponibles.

## 🧪 Pruebas

Las pruebas del backend usan pytest. Por defecto, la configuración cambia la base de datos de pruebas a SQLite; define `USE_POSTGRES_TESTS=true` para probar con PostgreSQL.

```powershell
cd backend
pip install -r ..\requirements-dev.txt
pytest
```

Para ejecutar las pruebas del frontend:

```powershell
cd frontend
npm test
```

## 🗂️ Estructura del repositorio

```text
.
├── backend/
│   ├── api/                 # Rutas, vistas, serializadores y servicios REST
│   ├── apps/                # Dominios: usuarios, cursos, actividades, juegos...
│   ├── auth/                # Autenticación, invitaciones y enlaces mágicos
│   ├── edunuñez/            # Configuración y enrutamiento de Django
│   └── manage.py
├── frontend/
│   └── src/                 # Aplicación React, páginas, componentes y servicios
├── docs/                    # Recursos y mockups
├── docker-compose.yml
├── .env.example
└── requirements-dev.txt
```

## 📖 Documentación adicional

- [Arquitectura del frontend](FRONTEND_ARCHITECTURE.md): estructura, rutas, autenticación y comunicación con la API.
- [Paleta de colores](PALETA_COLORES.md): colores y lineamientos visuales de la interfaz.
- [Variables de entorno](.env.example): referencia de configuración para desarrollo e integraciones.

---

<p align="center"><sub>EduNúñez · Proyecto de grado</sub></p>
