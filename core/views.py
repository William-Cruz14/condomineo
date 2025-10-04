from django.core.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import DjangoModelPermissions
from .models import Condominium, Visitor, Reservation, Apartment, Vehicle, Finance, Order, Visit
from django.db.models import Q
from .serializers import (
    VisitorSerializer, ReservationSerializer, ApartmentSerializer,
    VehicleSerializer, FinanceSerializer, OrderSerializer, VisitSerializer, CondominiumSerializer
)
from .permissions import IsOwnerOrAdmin
from .filters import (
    ApartmentFilter, VehicleFilter, FinanceFilter,
    ReservationFilter, VisitorFilter, OrderFilter, CondominiumFilter
)

class VisitorViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorSerializer
    permission_classes = [DjangoModelPermissions, IsOwnerOrAdmin]
    filterset_class = VisitorFilter
    search_fields = ('name', 'cpf')
    ordering_fields = ('name', 'cpf')

    def get_queryset(self):
        user = self.request.user
        query_base = Visitor.objects.select_related('condominium', 'registered_by', 'apartment')

        if user.user_type == 'admin':
            return query_base.filter(condominium__in=user.managed_condominiums.all())
        elif user.apartment:
            return query_base.filter(apartment=user.apartment)
        else:
            return query_base.filter(registered_by=user)

    def perform_create(self, serializer):
        condominium = None
        if self.request.user.apartment:
            condominium = self.request.user.apartment.condominium
        elif self.request.user.user_type == 'admin':
            condominium = serializer.validated_data.get('condominium')

        serializer.save(registered_by=self.request.user, condominium=condominium)

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [DjangoModelPermissions, IsOwnerOrAdmin]
    filterset_class = ReservationFilter
    search_fields = ('space',)
    ordering_fields = ('start_time', 'end_time')

    def get_queryset(self):
        user = self.request.user
        query_base = Reservation.objects.select_related('resident__apartment')

        if user.is_superuser:
            return query_base

        if user.user_type == 'admin':
            managed_condos = user.managed_condominiums.all()
            return query_base.filter(resident__apartment__condominium__in=managed_condos)

        if user.apartment:
            return query_base.filter(resident__apartment__condominium=user.apartment.condominium)

        return query_base.filter(resident=user)

    def perform_create(self, serializer):
        try:
            serializer.save(resident=self.request.user)
        except ValidationError as e:
            raise PermissionDenied(e.messages)

class ApartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsOwnerOrAdmin]
    serializer_class = ApartmentSerializer
    filterset_class = ApartmentFilter
    search_fields = ('number', 'block')
    ordering_fields = ('number', 'block', 'tread')

    def get_queryset(self):
        user = self.request.user
        query_base = Apartment.objects.select_related('condominium')

        if user.is_superuser:
            return query_base

        if user.user_type == 'admin':
            return query_base.filter(condominium__in=user.managed_condominiums.all())

        if user.user_type == 'resident' and user.apartment:
            return query_base.filter(id=user.apartment.id)

        return query_base.filter(residents=user)

    def perform_create(self, serializer):
        try:
            if self.request.user.user_type != 'admin':
                raise PermissionDenied("Apenas administradores podem criar apartamentos.")
            else:
                serializer.save()

        except ValidationError as e:
            raise PermissionDenied(e.messages)

class VisitViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsOwnerOrAdmin]
    serializer_class = VisitSerializer
    search_fields = ('visitor__name',)
    ordering_fields = ('entry_date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Visit.objects.select_related('visitor', 'apartment', 'registered_by')

        if user.user_type == 'admin':
            managed_condos = user.managed_condominiums.all()
            return query_base.filter(apartment__condominium__in=managed_condos)

        if user.apartment:
            return query_base.filter(apartment=user.apartment)

        return query_base.filter(registered_by=user)

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

class VehicleViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsOwnerOrAdmin]
    serializer_class = VehicleSerializer
    filterset_class = VehicleFilter
    search_fields = ('plate', 'model')
    ordering_fields = ('plate', 'model')

    def get_queryset(self):
        user = self.request.user
        query_base = Vehicle.objects.select_related('owner', 'condominium', 'registered_by')

        if user.is_superuser:
            return query_base

        if user.user_type == 'admin':
            return query_base.filter(condominium__in=user.managed_condominiums.all())
        elif user.user_type == 'resident':
            return query_base.filter(owner=user)
        else:
            return query_base.filter(registered_by=user)



    def perform_create(self, serializer):
        condominium = None
        if self.request.user.apartment:
            condominium = self.request.user.apartment.condominium
        elif self.request.user.user_type == 'admin':
            condominium = serializer.validated_data.get('condominium')

        serializer.save(registered_by=self.request.user, condominium=condominium)

class FinanceViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsOwnerOrAdmin]
    serializer_class = FinanceSerializer
    filterset_class = FinanceFilter
    search_fields = ('description',)
    ordering_fields = ('date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Finance.objects.select_related('creator', 'condominium')

        if user.is_superuser:
            return query_base

        if user.user_type == 'admin':
            return query_base.filter(condominium__in=user.managed_condominiums.all())

        if user.apartment:
            return query_base.filter(condominium=user.apartment.condominium)

        return query_base.filter(creator=user)

    def perform_create(self, serializer):
        condominium = None
        if self.request.user.apartment:
            condominium = self.request.user.apartment.condominium
        elif self.request.user.user_type == 'admin':
            condominium = serializer.validated_data.get('condominium')

        serializer.save(creator=self.request.user, condominium=condominium)

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsOwnerOrAdmin]
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    search_fields = ('order_code',)
    ordering_fields = ('order_date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Order.objects.select_related('owner', 'registered_by')

        if user.user_type == 'admin':
            managed_condos = user.managed_condominiums.all()
            return query_base.filter(owner__apartment__condominium__in=managed_condos)

        elif user.apartment:
            return query_base.filter(owner=user)
        else:
            return query_base.filter(registered_by=user)

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

# Adicionei um ViewSet para Condominium
class CondominiumViewSet(viewsets.ModelViewSet):
    permission_classes = [DjangoModelPermissions, IsOwnerOrAdmin]
    serializer_class = CondominiumSerializer
    filterset_class = CondominiumFilter
    search_fields = ('name', 'cnpj')
    ordering_fields = ('name',)

    def get_queryset(self):
        user = self.request.user
        query_base = Condominium.objects.all()

        if user.user_type == 'admin':
            return query_base.filter(Q(id__in=user.managed_condominiums.all()) | Q(created_by=user))

        if user.apartment:
            return query_base.filter(id=user.apartment.condominium.id)

        return Condominium.objects.none()

    def perform_create(self, serializer):
        if self.request.user.user_type != 'admin':
            raise PermissionDenied("Apenas administradores podem criar condomínios.")
        else:
            serializer.save(created_by=self.request.user)