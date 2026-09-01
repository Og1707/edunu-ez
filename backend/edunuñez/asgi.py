"""
ASGI config for edunuñez project.

Producción usa:
  DJANGO_SETTINGS_MODULE=edunuñez.settings.production
  uvicorn edunuñez.asgi:application --host 0.0.0.0 --port 8000
"""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edunuñez.settings.production")

application = get_asgi_application()
