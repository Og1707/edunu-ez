from rest_framework import status, viewsets, permissions
from rest_framework.exceptions import Throttled
from rest_framework.response import Response
from rest_framework.views import APIView

# Patrón seguro para vistas que no usan ViewSet:
# get_object_or_404(Model, pk=pk, user=request.user)
# Nunca haga primero get() y luego validate owner en dos pasos,
# porque eso puede filtrar recursos ajenos de forma insegura o masajear 404/403.
from .models import Invitation
from .serializers import InvitationSerializer
from .services import crear_magic_link, verificar_magic_link
from .mixins import IsOwnerOrDeny, OwnerQuerysetMixin
from .throttles import InvitacionRateThrottle


class MagicLinkRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            payload = crear_magic_link(request.data.get('email', '').strip())
            return Response(payload, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class MagicLinkVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.query_params.get('token', '').strip()
        try:
            payload = verificar_magic_link(token)
            return Response(payload, status=status.HTTP_200_OK)
        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class InvitacionViewSet(OwnerQuerysetMixin, viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrDeny]
    throttle_classes = [InvitacionRateThrottle]
    owner_field = 'created_by'

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def throttled(self, request, wait):
        raise Throttled(detail='Límite de invitaciones alcanzado. Intenta en 1 hora.')
