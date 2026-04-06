from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MagicLinkRequestView, MagicLinkVerifyView, InvitacionViewSet

router = DefaultRouter()
router.register(r'invitaciones', InvitacionViewSet, basename='invitacion')

urlpatterns = [
    path('magic-link/', MagicLinkRequestView.as_view(), name='magic_link_request'),
    path('magic-link/verify/', MagicLinkVerifyView.as_view(), name='magic_link_verify'),
    path('', include(router.urls)),
]
