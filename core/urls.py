from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import DjangoModelPermissions
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import (
    VisitorViewSet, ReservationViewSet, ApartmentViewSet,
    FinanceViewSet, VehicleViewSet, OrderViewSet, VisitViewSet, CondominiumViewSet
    )

router = DefaultRouter()
#router.register(r'users', UserViewSet, basename='user')
router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'apartments', ApartmentViewSet, basename='apartment')
router.register(r'finances', FinanceViewSet, basename='finance')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'visits', VisitViewSet, basename='visit')
router.register(r'condominiums', CondominiumViewSet, basename='condominium')

urlpatterns = [
    # Schema OpenAPI
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('v1/', include(router.urls)),
]