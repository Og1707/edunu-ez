from django.urls import path
from .views import *

urlpatterns = [
    path('api/registro/', RegistroView.as_view(), name='registro'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/olvide_contrasena/', OlvideContrasenaView.as_view(), name='olvide_contrasena'),
]



