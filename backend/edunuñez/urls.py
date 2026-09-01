"""
URL configuration — EduNúñez.

Endpoints de documentación:
  /api/schema/   → Esquema OpenAPI 3.x descargable (YAML/JSON)
  /api/docs/     → Swagger UI interactivo
  /api/redoc/    → ReDoc (documentación estilo referencia)
"""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
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
