"""
WSGI config for edunuñez project.

Producción usa:
  DJANGO_SETTINGS_MODULE=edunuñez.settings.production
  gunicorn edunuñez.wsgi:application --bind 0.0.0.0:8000 --workers 4
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "edunuñez.settings.production")

application = get_wsgi_application()
