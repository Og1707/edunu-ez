from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from auth.authentication import JWTAuthentication
from api.permissions import IsAdministrador, IsProfesor
from api.dashboard_serializers import DashboardStudentDetailSerializer, DashboardSummarySerializer
from api.services.dashboard_service import DashboardService


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def dashboard_summary(request):
    data = DashboardService.get_summary(request.user)
    return Response(DashboardSummarySerializer(data).data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication, SessionAuthentication])
@permission_classes([IsAuthenticated, IsProfesor | IsAdministrador])
def dashboard_student_detail(request, student_id):
    data = DashboardService.get_student_detail(request.user, student_id)
    return Response(DashboardStudentDetailSerializer(data).data, status=status.HTTP_200_OK)
