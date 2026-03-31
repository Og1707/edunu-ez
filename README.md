# Edunuñez Django

Proyecto de grado: plataforma educativa con backend Django y frontend React.

## Estructura

- `backend/`: aplicación Django principal
  - `manage.py`: comando de administración
  - `api/`: endpoints REST y lógica del proyecto
  - `edunuñez/`: configuración de Django
- `frontend/`: aplicación React
- `documentaciones/`: documentación del proyecto y guías

## Requisitos

- Python 3.11+ (o la versión que use tu entorno)
- Node.js 16+ / npm o yarn

## Configuración local

1. Abrir terminal en la raíz del proyecto.
2. Crear y activar un entorno virtual Python dentro de `backend/`.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instalar las dependencias Python.

```powershell
python -m pip install --upgrade pip
python -m pip install django djangorestframework django-cors-headers
```

> Si el proyecto tiene dependencias adicionales, agrégalas en el futuro a un archivo `backend/requirements.txt`.

4. Instalar dependencias del frontend.

```powershell
cd ..\frontend
npm install
```

## Ejecutar el backend

Desde `backend/`:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

## Ejecutar el frontend

Desde `frontend/`:

```powershell
cd frontend
npm start
```

## Verificar el proyecto

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:3000`

## Notas importantes

- El repositorio ya contiene documentación adicional en `documentaciones/`.
- Si usas GitHub, sube siempre solo el código fuente y evita incluir:
  - entornos virtuales (`.venv/`)
  - archivos de compilación de React (`frontend/build/`)
  - archivos temporales y de sistema

## Archivos clave

- `backend/api/views/`: vistas separadas por dominio
- `backend/api/urls.py`: rutas de la API
- `frontend/src/`: código de React
- `documentaciones/`: resúmenes, guías y notas del proyecto
