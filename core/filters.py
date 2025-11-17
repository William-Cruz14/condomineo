from django_filters import rest_framework as filters
from core.models import (
    Apartment, Vehicle, Finance, Reservation, Visitor, Order,
    Condominium, Communication, Notice, Visit, Resident, Occurrence
)
from django.db.models import Q

def getuser(request):
    return request.user

# Funções de filtro de queryset conforme o tipo de usuário
def queryset_filter_condominium(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros do condomínio que ele criou
    if user.user_type == "admin":
        return query_base.filter(pk__in=user.managed_condominiums.all())
    elif user.user_type == "employee": # Se for funcionário, retorna todos os registros do condomínio do funcionário
        return query_base.filter(pk=user.condominium.id)
    else: # Se for residente, retorna apenas os registros do condomínio do apartamento do residente
        return query_base.filter(pk=user.condominium.id)


def queryset_filter_apartment(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros do apartamento que ele criou
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    elif user.user_type == "employee":# Se for funcionário, retorna todos os registros do apartamento do condomínio do funcionário
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas os registros do apartamento do residente
        return query_base.filter(pk=user.apartment.id)


def queryset_filter_vehicle(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros do veículo que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    elif user.user_type == "employee":# Se for funcionário, retorna todos os registros do veículo do condomínio do funcionário
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas os registros do veículo do residente
        return query_base.filter(owner=user)


def queryset_filter_visitor(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros do visitante que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    elif user.user_type == "employee":# Se for funcionário, retorna todos os registros do visitante do condomínio do funcionário
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas os registros do visitante do apartamento do residente
        return query_base.filter(Q(registered_by=user) | Q(apartment=user.apartment))


def queryset_filter_visit(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros da visita que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    elif user.user_type == "employee":# Se for funcionário, retorna todos os registros da visita do condomínio do funcionário
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas os registros da visita do apartamento do residente
        return query_base.filter(Q(apartment=user.apartment) | Q(registered_by=user))



def queryset_filter_reservation(query_base, user):
    """Filtra o queryset para reservas conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros da reserva que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    # Se for funcionário, retorna todos os registros da reserva do condomínio do funcionário
    elif user.user_type == "employee":
        return query_base.filter(condominium=user.condominium)
    # Se for residente, retorna apenas os registros da reserva do residente
    else:
        return query_base.filter(resident=user)


def queryset_filter_resident(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros do residente que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    elif user.user_type == "employee":# Se for funcionário, retorna todos os registros do residente do condomínio do funcionário
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas o registro do residente
        return query_base.filter(Q(registered_by=user) | Q(apartment=user.apartment))



def queryset_filter_finance(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros da finança que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    # Se for funcionário, retorna todos os registros da finança do condomínio do funcionário
    elif user.user_type == "employee":
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas os registros da finança do condomínio do apartamento do residente
        return query_base.filter(condominium=user.apartment.condominium)



def queryset_filter_order(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros do pedido que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    elif user.user_type == "employee":# Se for funcionário, retorna todos os registros do pedido do condomínio do funcionário
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas os registros do pedido do residente
        return query_base.filter(owner=user)

def queryset_filter_notice(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros do aviso que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    elif user.user_type == "employee":# Se for funcionário, retorna todos os registros do aviso do condomínio do funcionário
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas os registros do aviso do condomínio do apartamento do residente
        return query_base.filter(condominium=user.apartment.condominium)


def queryset_filter_communication(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # O usuário deve ver comunicações que ele enviou OU recebeu,
    # mas apenas dentro dos condomínios aos quais ele tem acesso.
    user_is_participant = Q(sender=user) | Q(recipients=user)

    if user.user_type == "admin":
        # Comunicações nos condomínios que o admin gerencia
        condominium_filter = Q(condominium__in=user.managed_condominiums.all())
        return query_base.filter(condominium_filter & user_is_participant).distinct()

    elif user.user_type == "employee":
        # Comunicações no condomínio do funcionário
        condominium_filter = Q(condominium=user.condominium)
        return query_base.filter(condominium_filter & user_is_participant).distinct()

    else:  # resident
        # Comunicações no condomínio do morador
        condominium_filter = Q(condominium=user.condominium)
        return query_base.filter(condominium_filter & user_is_participant).distinct()


def queryset_filter_occurrence(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todos os registros da ocorrência que esteja no condomínio que ele gerencia
    if user.user_type == "admin":
        return query_base.filter(condominium__in=user.managed_condominiums.all())
    elif user.user_type == "employee":# Se for funcionário, retorna todos os registros da ocorrência do condomínio do funcionário
        return query_base.filter(condominium=user.condominium)
    else: # Se for residente, retorna apenas os registros da ocorrência do apartamento do residente
        return query_base.filter(reported_by=user)

# Filtros para os ViewSets, usando django-filters para facilitar a filtragem via query parameters
class ApartmentFilter(filters.FilterSet):
    number = filters.CharFilter(field_name='number', lookup_expr='iexact')
    block = filters.CharFilter(field_name='block', lookup_expr='iexact')
    tread = filters.NumberFilter(field_name='tread')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Apartment
        fields = ['number', 'block', 'tread', 'condominium']


class VehicleFilter(filters.FilterSet):
    plate = filters.CharFilter(field_name='plate', lookup_expr='iexact')
    owner = filters.NumberFilter(field_name='owner')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Vehicle
        fields = ['plate', 'owner', 'condominium']


class FinanceFilter(filters.FilterSet):
    date_after = filters.DateTimeFilter(field_name='date', lookup_expr='gte')
    date_before = filters.DateTimeFilter(field_name='date', lookup_expr='lte')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Finance
        fields = ['date_after', 'date_before', 'condominium']


class ReservationFilter(filters.FilterSet):
    start_after = filters.DateTimeFilter(field_name='start_time', lookup_expr='gte')
    start_before = filters.DateTimeFilter(field_name='start_time', lookup_expr='lte')
    space = filters.CharFilter(field_name='space', lookup_expr='iexact')
    resident = filters.NumberFilter(field_name='resident')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Reservation
        fields = ['start_after', 'start_before', 'space', 'resident', 'condominium']


class VisitorFilter(filters.FilterSet):
    document = filters.CharFilter(field_name='cpf', lookup_expr='iexact')
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Visitor
        fields = ['cpf', 'name', 'condominium']


class OrderFilter(filters.FilterSet):
    order_code = filters.CharFilter(field_name='order_code', lookup_expr='icontains')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    owner = filters.NumberFilter(field_name='owner')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Order
        fields = ['order_code', 'status', 'owner', 'condominium']


class CondominiumFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    cnpj = filters.CharFilter(field_name='cnpj', lookup_expr='iexact')

    class Meta:
        model = Condominium
        fields = ['name', 'cnpj']

class CommunicationFilter(filters.FilterSet):
    subject = filters.CharFilter(field_name='subject', lookup_expr='icontains')
    sender = filters.NumberFilter(field_name='sender')
    communication_type = filters.CharFilter(field_name='communication_type', lookup_expr='iexact')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Communication
        fields = ['subject', 'sender', 'condominium', 'communication_type']


class NoticeFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Notice
        fields = ['title', 'condominium']


class VisitFilter(filters.FilterSet):
    visitor_name = filters.CharFilter(field_name='visitor__name', lookup_expr='icontains')
    apartment_number = filters.CharFilter(field_name='apartment__number', lookup_expr='iexact')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Visit
        fields = ['visitor_name', 'apartment_number', 'condominium']


class ResidentFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    apartment_number = filters.CharFilter(field_name='apartment__number', lookup_expr='iexact')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Resident
        fields = ['name', 'apartment_number', 'condominium']



class OccurrenceFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')
    status = filters.CharFilter(field_name='status', lookup_expr='iexact')
    reported_by = filters.NumberFilter(field_name='reported_by')
    condominium = filters.NumberFilter(field_name='condominium')

    class Meta:
        model = Occurrence
        fields = ['title', 'status', 'reported_by', 'condominium']


