"""
URLs del módulo auth — EduNúñez.

Endpoints disponibles:
  POST  /auth/magic-link/          → Solicitar magic link
  GET   /auth/magic-link/verify/   → Verificar token y obtener JWT
  POST  /auth/token/refresh/       → Rotar access token con refresh token (simplejwt)
  POST  /auth/token/blacklist/     → Invalidar refresh token (logout)
  CRUD  /auth/invitaciones/        → Gestión de invitaciones (autenticado)
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views import InvitacionViewSet, MagicLinkRequestView, MagicLinkVerifyView

router = DefaultRouter()
router.register(r"invitaciones", InvitacionViewSet, basename="invitacion")

urlpatterns = [
    # Magic Link
    path("magic-link/", MagicLinkRequestView.as_view(), name="magic_link_request"),
    path("magic-link/verify/", MagicLinkVerifyView.as_view(), name="magic_link_verify"),
    # Rotación y blacklist de tokens JWT (simplejwt)
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # Invitaciones
    path("", include(router.urls)),
]
