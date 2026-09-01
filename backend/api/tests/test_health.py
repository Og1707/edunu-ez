"""
Tests del endpoint /api/health/ — EduNúñez.
"""
from unittest.mock import patch

from django.db import OperationalError as DbOperationalError
from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckTests(APITestCase):
    """Tests del endpoint GET /api/health/."""

    URL = "/api/health/"

    def test_health_check_ok_retorna_200(self):
        """Cuando DB y Redis están ok, el endpoint retorna 200 con status ok."""
        response = self.client.get(self.URL)

        # En tests, DB es SQLite (siempre up) y Redis es LocMemCache (siempre up).
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")
        self.assertTrue(response.data["db"])
        self.assertTrue(response.data["redis"])
        self.assertIn("version", response.data)

    def test_health_check_no_requiere_autenticacion(self):
        """El endpoint debe ser accesible sin token JWT."""
        # client no tiene autenticación configurada por defecto
        response = self.client.get(self.URL)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("api.views.health._check_db", return_value=(False, "Connection refused"))
    def test_health_check_db_down_retorna_503(self, _mock_db):
        """Si la DB falla, el endpoint retorna 503 con status degraded."""
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["status"], "degraded")
        self.assertFalse(response.data["db"])
        self.assertIn("errors", response.data)

    @patch("api.views.health._check_redis", return_value=(False, "Redis unavailable"))
    def test_health_check_redis_down_retorna_503(self, _mock_redis):
        """Si Redis falla, el endpoint retorna 503."""
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
        self.assertEqual(response.data["status"], "degraded")
        self.assertFalse(response.data["redis"])
