import json
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class RecipientWebhooks(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        try:
            payload = request.data
        except Exception:
            payload = json.loads(request.body.decode('utf-8'))

        logger.info('Webhook recibido: %s', payload)
        return Response({'mensaje': 'Webhook recibido'}, status=status.HTTP_200_OK)
