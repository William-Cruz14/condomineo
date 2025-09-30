from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.routers import DefaultRouter
from .views import PersonView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()

router.register(r'persons', PersonView, basename='person')


schema_view = get_schema_view(
    openapi.Info(
        title="Condomineo API",
        default_version='v1',
        description="API de um sistema de gestão de condomínio",
    ),
    public=True,
    permission_classes=[DjangoModelPermissions,],
)

urlpatterns = [
    path('api/auth/', TokenObtainPairView.as_view()),
    path('api-auth/refresh', TokenRefreshView.as_view()),
    path('', include(router.urls)),
]