from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    VisitorViewSet, ReservationViewSet, ApartmentViewSet,
    FinanceViewSet, VehicleViewSet, OrderViewSet, VisitViewSet,
    CondominiumViewSet, ResidentViewSet, NoticeViewSet, CommunicationViewSet
)

router = DefaultRouter()

router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'apartments', ApartmentViewSet, basename='apartment')
router.register(r'finances', FinanceViewSet, basename='finance')
router.register(r'notices', NoticeViewSet, basename='notice')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'visits', VisitViewSet, basename='visit')
router.register(r'residents', ResidentViewSet, basename='resident')
router.register(r'condominiums', CondominiumViewSet, basename='condominium')
router.register(r'communications', CommunicationViewSet, basename='communication')

urlpatterns = [
    path('', include(router.urls)),
]