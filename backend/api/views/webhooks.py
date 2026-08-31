import json
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers import PartidaJuegoWebhookSerializer

logger = logging.getLogger(__name__)


class RecipientWebhooks(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            payload = request.data
        except Exception:
            payload = json.loads(request.body.decode('utf-8'))

        logger.info('🎯 Webhook recibido desde n8n: %s', payload)

        # Pasamos los datos al serializador para guardarlos
        serializer = PartidaJuegoWebhookSerializer(data=payload)
        
        if serializer.is_valid():
            serializer.save() # ¡Aquí se guarda en PostgreSQL!
            return Response({
                'mensaje': 'Webhook recibido y partida guardada exitosamente'
            }, status=status.HTTP_201_CREATED)
        else:
            logger.error("❌ Error en los datos del webhook: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

