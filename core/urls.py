from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CustomAuthToken, UserViewSet, VisitorViewSet,
                   ReservationViewSet, CommunicationViewSet, ApartmentViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'visitors', VisitorViewSet, basename='visitor')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'communications', CommunicationViewSet, basename='communication')
router.register(r'apartments', ApartmentViewSet, basename='apartment')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', CustomAuthToken.as_view()),
    path('api-auth/', include('rest_framework.urls')),  # login/logout para navegador
]