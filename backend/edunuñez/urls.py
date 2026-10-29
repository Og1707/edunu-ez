"""
URL configuration — EduNúñez.

Endpoints de documentación:
  /api/schema/   → Esquema OpenAPI 3.x descargable (YAML/JSON)
  /api/docs/     → Swagger UI interactivo
  /api/redoc/    → ReDoc (documentación estilo referencia)
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def api_root_view(request):
    """
    Vista raíz informativa para la API de EduNúñez.
    Retorna estado del backend, enlaces a Swagger/ReDoc y referencia al frontend.
    """
    return JsonResponse({
        "plataforma": "EduNúñez API",
        "version": "2.0.0",
        "estado": "operativo",
        "documentacion": {
            "swagger": "/api/docs/",
            "redoc": "/api/redoc/",
            "openapi_schema": "/api/schema/",
        },
        "endpoints_principales": {
            "health": "/api/health/",
            "admin": "/admin/",
            "cursos": "/api/cursos/",
            "actividades": "/api/actividades/",
            "auth": "/auth/",
        },
        "frontend": "http://localhost:3000/",
        "mensaje": "Servidor backend de EduNúñez activo. El frontend interactivo se ejecuta en http://localhost:3000",
    })


urlpatterns = [
    # Raíz del backend (API Root informativa)
    path("", api_root_view, name="api-root"),

    # Admin
    path("admin/", admin.site.urls),

    # API principal
    path("api/", include("api.urls")),

    # Auth (magic link, invitaciones, token refresh/blacklist)
    path("auth/", include("auth.urls")),

    # ---------------------------------------------------------------
    # OpenAPI / Swagger — disponible solo con DEBUG=True en producción
    # se puede restringir añadiendo permission_classes=[IsAdminUser] en
    # SpectacularSwaggerView si se desea.
    # ---------------------------------------------------------------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

