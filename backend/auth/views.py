"""
Vistas de autenticación — EduNúñez.

Incluye:
  - MagicLinkRequestView  → POST /auth/magic-link/
  - MagicLinkVerifyView   → GET  /auth/magic-link/verify/?token=...
  - InvitacionViewSet     → CRUD /auth/invitaciones/
"""
from rest_framework import status, viewsets, permissions
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Invitation
from .serializers import InvitationSerializer
from .services import crear_magic_link, verificar_magic_link
from .mixins import IsOwnerOrDeny, OwnerQuerysetMixin
from .throttles import InvitacionRateThrottle


class MagicLinkRequestView(APIView):
    """
    Solicita un magic link para el email dado.

    POST /auth/magic-link/
    Body: { "email": "usuario@ejemplo.com" }
    Response 200: { "mensaje": "..." }
    Response 400: { "error": "..." }
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()
        try:
            payload = crear_magic_link(email)
            return Response(payload, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class MagicLinkVerifyView(APIView):
    """
    Verifica el magic link y emite tokens JWT (access + refresh).

    GET /auth/magic-link/verify/?token=<uuid>
    Response 200: {
        "access": "...",
        "refresh": "...",
        "usuario_id": ...,
        "email": "...",
        "rol": "..."
    }
    Response 400: { "error": "..." }
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.query_params.get("token", "").strip()
        try:
            payload = verificar_magic_link(token)
            return Response(payload, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class InvitacionViewSet(OwnerQuerysetMixin, viewsets.ModelViewSet):
    """
    CRUD de invitaciones.
    Sólo el creador puede ver/editar/eliminar sus propias invitaciones (IsOwnerOrDeny).
    Limitado a 10 invitaciones/hora por usuario (InvitacionRateThrottle).
    """

    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrDeny]
    throttle_classes = [InvitacionRateThrottle]
    owner_field = "created_by"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def throttled(self, request, wait):
        raise Throttled(detail="Límite de invitaciones alcanzado. Intenta en 1 hora.")
