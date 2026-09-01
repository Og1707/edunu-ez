"""
Tests del endpoint OpenAPI/Swagger — EduNúñez.

Verifica que drf-spectacular genera un esquema válido y accesible.
"""
from rest_framework import status
from rest_framework.test import APITestCase


class OpenAPISchemaTests(APITestCase):
    """Tests de los endpoints de documentación OpenAPI."""

    def test_schema_endpoint_retorna_200(self):
        """GET /api/schema/ debe retornar 200 con el esquema YAML."""
        response = self.client.get("/api/schema/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schema_contiene_openapi_version(self):
        """El esquema debe ser OpenAPI 3.x."""
        response = self.client.get("/api/schema/", HTTP_ACCEPT="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El contenido puede ser YAML o JSON según el Accept header
        content = response.content.decode("utf-8")
        self.assertIn("openapi", content.lower())

    def test_swagger_ui_retorna_200(self):
        """GET /api/docs/ debe retornar la página de Swagger UI."""
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_redoc_retorna_200(self):
        """GET /api/redoc/ debe retornar la página de ReDoc."""
        response = self.client.get("/api/redoc/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_schema_incluye_endpoint_health(self):
        """El esquema debe incluir el endpoint /api/health/."""
        response = self.client.get("/api/schema/", HTTP_ACCEPT="application/json")
        content = response.content.decode("utf-8")
        self.assertIn("/api/health/", content)

    def test_schema_incluye_endpoint_login(self):
        """El esquema debe incluir el endpoint de login."""
        response = self.client.get("/api/schema/", HTTP_ACCEPT="application/json")
        content = response.content.decode("utf-8")
        self.assertIn("login", content.lower())
