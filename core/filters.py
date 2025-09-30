from django_filters import rest_framework as filters
from .models import Apartment, Vehicle, Finance, Reservation, Visitor, Order, Condominium


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

    class Meta:
        model = Reservation
        fields = ['start_after', 'start_before', 'space', 'resident']


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

    class Meta:
        model = Order
        fields = ['order_code', 'status', 'owner']


class CondominiumFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    cnpj = filters.CharFilter(field_name='cnpj', lookup_expr='iexact')

    class Meta:
        model = Condominium
        fields = ['name', 'cnpj']
