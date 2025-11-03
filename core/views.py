from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated, IsAdminUser
from .models import (
    Condominium, Visitor, Reservation, Apartment,
    Vehicle, Finance, Order, Visit, Resident, Notice, Communication
)

from .serializers import (
    VisitorSerializer, ReservationSerializer, ApartmentSerializer,
    VehicleSerializer, FinanceSerializer, OrderSerializer, VisitSerializer,
    CondominiumSerializer, ResidentSerializer,
    NoticeSerializer, CommunicationSerializer
)
from .permissions import IsOwnerOrAdmin, IsResident
from .filters import (
    ApartmentFilter, VehicleFilter, FinanceFilter,
    ReservationFilter, VisitorFilter, OrderFilter, CondominiumFilter, VisitFilter,
    queryset_filter_condominium, queryset_filter_apartment, queryset_filter_vehicle, queryset_filter_visitor,
    queryset_filter_visit, queryset_filter_reservation, queryset_filter_resident, queryset_filter_finance,
    queryset_filter_order, queryset_filter_notice, queryset_filter_communication, NoticeFilter, ResidentFilter,
    CommunicationFilter
)

class VisitorViewSet(viewsets.ModelViewSet):
    serializer_class = VisitorSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filterset_class = VisitorFilter
    search_fields = ('name', 'cpf')
    ordering_fields = ('name', 'cpf')

    def get_queryset(self):
        user = self.request.user
        query_base = Visitor.objects.select_related('condominium', 'registered_by', 'apartment')
        return queryset_filter_visitor(query_base, user)


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filterset_class = ReservationFilter
    search_fields = ('space',)
    ordering_fields = ('start_time', 'end_time')

    def get_queryset(self):
        user = self.request.user
        query_base = Reservation.objects.select_related('resident__apartment')
        return queryset_filter_reservation(query_base, user)


class ApartmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ApartmentSerializer
    filterset_class = ApartmentFilter
    search_fields = ('number', 'block')
    ordering_fields = ('number', 'block', 'tread')

    def get_queryset(self):
        user = self.request.user
        query_base = Apartment.objects.select_related('condominium')
        return queryset_filter_apartment(query_base, user)

class ResidentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = ResidentSerializer
    filterset_class = ResidentFilter
    search_fields = ('registered_by__name',)

    def get_queryset(self):
        user = self.request.user
        query_base = Resident.objects.select_related('registered_by', 'apartment')
        return queryset_filter_resident(query_base, user)

class VisitViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = VisitSerializer
    filterset_class = VisitFilter
    search_fields = ('visitor__name',)
    ordering_fields = ('entry_date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Visit.objects.select_related('visitor', 'apartment', 'registered_by')
        return queryset_filter_visit(query_base, user)

class VehicleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = VehicleSerializer
    filterset_class = VehicleFilter
    search_fields = ('plate', 'model')
    ordering_fields = ('plate', 'model')

    def get_queryset(self):
        user = self.request.user
        query_base = Vehicle.objects.select_related('owner', 'condominium', 'registered_by')
        return queryset_filter_vehicle(query_base, user)

class FinanceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = FinanceSerializer
    filterset_class = FinanceFilter
    search_fields = ('description',)
    ordering_fields = ('date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Finance.objects.select_related('creator', 'condominium')
        return queryset_filter_finance(query_base, user)


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = OrderSerializer
    filterset_class = OrderFilter
    search_fields = ('order_code',)
    ordering_fields = ('order_date',)

    def get_queryset(self):
        user = self.request.user
        query_base = Order.objects.select_related('owner', 'registered_by')
        return queryset_filter_order(query_base, user)


# Adicionei um ViewSet para Condominium
class CondominiumViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = CondominiumSerializer
    filterset_class = CondominiumFilter
    search_fields = ('name', 'cnpj')
    ordering_fields = ('name',)


    def get_queryset(self):
        user = self.request.user
        query_base = Condominium.objects.all()
        return queryset_filter_condominium(query_base, user)


class NoticeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = NoticeSerializer
    filterset_class = NoticeFilter
    search_fields = ('title',)
    ordering_fields = ('created_at',)

    def get_queryset(self):
        user = self.request.user
        query_base = Notice.objects.select_related('author', 'condominium')
        return queryset_filter_notice(query_base, user)


class CommunicationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = CommunicationSerializer
    filterset_class = CommunicationFilter
    search_fields = ('sender', 'recipients__name')

    def get_queryset(self):
        user = self.request.user
        query_base = Communication.objects.select_related('sender', 'condominium').prefetch_related('recipients')
        return queryset_filter_communication(query_base, user)

def home(request):
    from django.shortcuts import render
    return render(request, 'pages/home.html', {})