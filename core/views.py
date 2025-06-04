from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.db.models import Q

from .models import CustomUser, Visitor, Reservation, Communication, Apartment, Vehicle, Finance, Orders, Visit
from .serializers import (
    CustomUserSerializer, CustomUserCreateSerializer, VisitorSerializer,
    ReservationSerializer, CommunicationSerializer, ApartmentSerializer, VehicleSerializer, FinanceSerializer,
    OrdersSerializer)


# Autenticação por token
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'user_id': user.pk,
                'email': user.email,
                'name': user.name,
                'user_type': user.user_type,
            }

        })

# ViewSets para o modelo CustomUser, Visitor, Reservation, Communication e Apartment
class UserViewSet(viewsets.ModelViewSet):
    serializer_class = CustomUserSerializer
    permission_classes = [DjangoModelPermissions,]
    # Sobrescrevendo o método get_serializer_class para retornar o CustomUserCreateSerializer quando a ação for 'create'
    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return super().get_serializer_class()

    # Sobrescreve o método get_queryset para filtrar os usuários de acordo com o usuário logado
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
    permission_classes = [DjangoModelPermissions,]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Visitor.objects.all()
        return Visitor.objects.filter(registered_by=user)

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [DjangoModelPermissions,]

    # Sobrescreve o método get_queryset para filtrar as reservas de acordo com o usuário logado
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(resident=user)

    # Sobrescreve o método perform_create para salvar o usuário logado como o criador da reserva.
    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)


class CommunicationViewSet(viewsets.ModelViewSet):
    serializer_class = CommunicationSerializer
    permission_classes = [DjangoModelPermissions,]

    # Sobrescreve o método get_queryset para filtrar as comunicações de acordo com o usuário logado
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Communication.objects.all()
        return Communication.objects.filter(
            Q(sender=user) | Q(recipients=user)
        )

    # Sobrescreve o método perform_create para salvar o usuário logado como o criador da comunicação.
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

class ApartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions,]
    serializer_class = ApartmentSerializer

    # Sobrescreve o método get_queryset para filtrar os apartamentos de acordo com o usuário logado
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Apartment.objects.all()
        return Apartment.objects.filter(residents=user)

    # Sobrescreve o método perform_create para salvar o usuário logado como o criador do apartamento.
    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

class VisitViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions,]
    serializer_class = VisitorSerializer

    # Sobrescreve o método get_queryset para filtrar as visitas de acordo com o usuário logado
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Visit.objects.all()
        return Visit.objects.filter(resident=user)

    # Sobrescreve o método perform_create para salvar o usuário logado como o criador da visita.
    def perform_create(self, serializer):
        serializer.save(resident=self.request.user)
class VehicleViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions,]
    serializer_class = VehicleSerializer

    # Sobrescreve o método get_queryset para filtrar os veículos de acordo com o usuário logado
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Vehicle.objects.all()
        return Vehicle.objects.filter(owner=user)

    # Sobrescreve o método perform_create para salvar o usuário logado como o criador do veículo.
    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

class FinanceViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions,]
    serializer_class = FinanceSerializer

    # Sobrescreve o método get_queryset para filtrar as finanças de acordo com o usuário logado
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Finance.objects.all()
        return Finance.objects.filter(creator=user)

    # Sobrescreve o método perform_create para salvar o usuário logado como o criador da finança.
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class OrdersViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions,]
    serializer_class = OrdersSerializer

    # Sobrescreve o método get_queryset para filtrar os pedidos de acordo com o usuário logado
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Orders.objects.all()
        return Orders.objects.filter(creator=user)

    # Sobrescreve o método perform_create para salvar o usuário logado como o criador do pedido.
    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)