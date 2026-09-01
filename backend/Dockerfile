# ============================================================
# Dockerfile multi-stage — EduNúñez Backend
# ============================================================
#
# Stage 1 (builder):  Instala dependencias Python en un directorio aislado.
# Stage 2 (production): Imagen final liviana, sin build tools, usuario no-root.
#
# Build:
#   docker build -t edununez-backend:latest ./backend
#
# Run (desarrollo local con docker compose):
#   docker compose up backend
# ============================================================

# ---------------------------------------------------------------------------
# Stage 1 — Builder: instala dependencias
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Evitar archivos .pyc y buffering innecesario
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

# Copiar solo los manifiestos de dependencias para aprovechar el layer cache.
# Si no cambia requirements.txt, Docker no reinstala nada.
COPY requirements.txt .

# Instalar dependencias en /install para copiarlas al stage final.
# --no-cache-dir reduce el tamaño de la imagen.
RUN pip install --upgrade pip==24.0 \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------------------------------------------------------------------------
# Stage 2 — Production: imagen final liviana
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS production

# Variables de entorno de Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Por defecto usa production settings; sobreescribir en docker-compose
    DJANGO_SETTINGS_MODULE=edunuñez.settings.production \
    # Puerto de Gunicorn
    PORT=8000

# Instalar dependencias del sistema mínimas necesarias en runtime.
# libpq-dev es requerido por psycopg (cliente PostgreSQL).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar las dependencias Python del stage builder
COPY --from=builder /install /usr/local

# Crear usuario no-root para ejecutar la aplicación
RUN groupadd --gid 1001 appgroup \
    && useradd --uid 1001 --gid appgroup --shell /bin/bash --create-home appuser

# Directorio de trabajo
WORKDIR /app

# Copiar el código fuente
COPY --chown=appuser:appgroup . .

# Crear directorio para archivos estáticos recolectados
RUN mkdir -p /app/staticfiles && chown appuser:appgroup /app/staticfiles

# Cambiar al usuario no-root
USER appuser

# Recolectar estáticos durante el build (requiere DJANGO_SECRET_KEY dummy)
# En producción se sobreescribe con la key real via variable de entorno.
RUN DJANGO_SECRET_KEY=build-phase-dummy-key-not-used-at-runtime \
    DJANGO_SETTINGS_MODULE=edunuñez.settings.production \
    DJANGO_ALLOWED_HOSTS=localhost \
    DATABASE_URL=postgres://x:x@localhost/x \
    python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE 8000

# Healthcheck interno del contenedor
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health/ || exit 1

# Gunicorn con 4 workers (ajustar según CPU disponible)
CMD ["sh", "-c", \
    "gunicorn edunuñez.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers 4 \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --timeout 60 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile -"]
