from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.routers import DefaultRouter
from .views import (CustomAuthToken, UserViewSet, VisitorViewSet,
                    ReservationViewSet, CommunicationViewSet, ApartmentViewSet, FinanceViewSet, VehicleViewSet,
                    OrdersViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'communications', CommunicationViewSet, basename='communication')
router.register(r'apartments', ApartmentViewSet, basename='apartment')
router.register(r'finances', FinanceViewSet, basename='finance')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'orders', OrdersViewSet, basename='orders')

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
    # Documentação da API com Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # Documentação da API com ReDoc
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/', include(router.urls)),
    path('api/auth/', CustomAuthToken.as_view()),
    path('api-auth/', include('rest_framework.urls')),  # login/logout para navegador
]