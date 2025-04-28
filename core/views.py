from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.db import models

from .models import CustomUser, Visitor, Reservation, Communication, Apartment
from .serializers import (CustomUserSerializer, CustomUserCreateSerializer, VisitorSerializer, ReservationSerializer,
                          CommunicationSerializer, ApartmentSerializer)


# Autenticação personalizada
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'name': user.name,
            'user_type': user.user_type
        })

# ViewSets para o modelo CustomUser, Visitor, Reservation, Communication e Apartment
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

    @action(detail=False, methods=['get', 'put'], url_path='me')
    def me(self, request):
        user = self.request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def apartment(self, request, pk=None):
        user = request.user
        serializer = ApartmentSerializer(user.apartment, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

class VisitorViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Visitor.objects.all()
        return Visitor.objects.filter(apartment=user.apartment)

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(resident=user)

    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)


class CommunicationViewSet(viewsets.ModelViewSet):
    serializer_class = CommunicationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type in ['sindico', 'admin']:
            return Communication.objects.all()
    # Moradores veem apenas mensagens enviadas ou recebidas por eles
        else:
            # Filtra mensagens enviadas ou recebidas pelo usuário
            return Communication.objects.filter(
                models.Q(sender=user) | models.Q(recipient=user)
            )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class ApartmentViewSet(viewsets.ModelViewSet):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentSerializer
