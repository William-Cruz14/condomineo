from django.db.models import Q
from django_filters import rest_framework as filters
from users.models import Person

def queryset_filter_person(query_base, user):
    """Filtra o queryset conforme o tipo de usuário."""

    # Se o usuário for administrador, retorna todas as pessoas do condomínio que ele gerencia
    if user.user_type == 'admin':
        return query_base.filter(
            Q(pk=user.id) | Q(condominium__in=user.managed_condominiums.all())

        )
    elif user.user_type == "employee":  # Se for funcionário, retorna pessoas do condomínio do funcionário
        return query_base.filter(
            Q(condominium=user.condominium)
        )
    else: # Se for morador, retorna apenas ele e pessoas do seu apartamento
        return query_base.filter(
            Q(pk=user.id) | Q(apartment=user.apartment)
        )

class PersonFilterSet(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')
    cpf = filters.CharFilter(field_name='cpf', lookup_expr='icontains')
    user_type = filters.CharFilter(field_name='user_type', lookup_expr='iexact')
    condominium = filters.NumberFilter(field_name='condominium__id', lookup_expr='exact')
    apartment = filters.NumberFilter(field_name='apartment__id', lookup_expr='exact')

    class Meta:
        model = Person
        fields = ['name', 'email', 'cpf', 'user_type', 'condominium', 'apartment']