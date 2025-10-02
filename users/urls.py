from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonView

router = DefaultRouter()

router.register(r'persons', PersonView, basename='person')

urlpatterns = [
    path('', include(router.urls)),
]