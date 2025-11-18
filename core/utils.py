from django.db import models
from rest_framework.exceptions import ValidationError

from core.filters import getuser
from core.models import Condominium
from users.models import Person


def get_condominium_to_code(code):
    """Retorna o condomínio correspondente ao código fornecido."""
    try:
        condominium = Condominium.objects.get(code_condominium__iexact=code)
        return condominium
    except Condominium.DoesNotExist:
        raise ValidationError("Condomínio não encontrado para o código fornecido.")


def get_apartment_number(condominium, number, block):
    """Retorna o apartamento correspondente ao número e bloco fornecidos dentro do condomínio."""
    try:
        apartment = condominium.apartments.get(number=number, block__iexact=block)
        return apartment
    except condominium.apartments.model.DoesNotExist:
        raise ValidationError("Apartamento não encontrado no condomínio especificado.")


def pop_apartment_and_condominium(validated_data):
    """Extrai e retorna o apartamento e condomínio dos dados fornecidos."""
    code_condominium = validated_data.pop('code_condominium', None)
    apartment_number = validated_data.pop('number_apartment', None)
    apartment_block = validated_data.pop('block_apartment', None)

    if not all([apartment_number, apartment_block]):
        return code_condominium, None, None

    return code_condominium, apartment_number, apartment_block

def get_user_condo_apartment(context, validated_data):

    user = getuser(context['request'])

    code, apt_number, apt_block = pop_apartment_and_condominium(validated_data)

    if not user.is_anonymous and context['request'].method == 'POST':
        if user.user_type == Person.UserType.ADMIN and not code:
            raise ValidationError(
                "Código do condomínio é obrigatório para administradores."
            )

        if code:
            condominium = get_condominium_to_code(code)
            if apt_block and apt_number:
                apartment = get_apartment_number(condominium, apt_number, apt_block)
            else :
                apartment = None
        else:
            if user.user_type == Person.UserType.EMPLOYEE:
                if apt_number and apt_block:
                    apartment = get_apartment_number(user.condominium, apt_number, apt_block)
                    condominium = user.condominium
                else:
                    apartment = None
                    condominium = user.condominium
            else:
                apartment = user.apartment
                condominium = user.condominium

    else:
        if code:
            condominium = get_condominium_to_code(code)
            if apt_block and apt_number:
                apartment = get_apartment_number(condominium, apt_number, apt_block)
            else :
                apartment = None
        else:
            condominium = None
            apartment = None


    return user, condominium, apartment

