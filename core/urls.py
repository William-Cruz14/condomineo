from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitorViewSet, ReservationViewSet, ApartmentViewSet,
    FinanceViewSet, VehicleViewSet, OrderViewSet, VisitViewSet,
    CondominiumViewSet, ResidentViewSet, ResidentAdminViewSet,
    ReservationAdminViewSet
)

router = DefaultRouter()

router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'reservations-admin', ReservationAdminViewSet, basename='admin-reservation')
router.register(r'apartments', ApartmentViewSet, basename='apartment')
router.register(r'finances', FinanceViewSet, basename='finance')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'visits', VisitViewSet, basename='visit')
router.register(r'residents', ResidentViewSet, basename='resident')
router.register(r'residents-admin', ResidentAdminViewSet, basename='admin-resident')
router.register(r'condominiums', CondominiumViewSet, basename='condominium')

urlpatterns = [
    path('', include(router.urls)),
]