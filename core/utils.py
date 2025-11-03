from django.db import models
from core.models import Condominium

def get_condominium_to_code(code):
    """Retorna o condomínio correspondente ao código fornecido."""
    try:
        condominium = Condominium.objects.get(code_condominium__iexact=code)
        return condominium
    except Condominium.DoesNotExist:
        return "Condomínio não encontrado."


def get_apartment_number(condominium, number, block):
    """Retorna o apartamento correspondente ao número e bloco fornecidos dentro do condomínio."""
    try:
        apartment = condominium.apartments.get(number=number, block__iexact=block)
        return apartment
    except condominium.apartments.model.DoesNotExist:
        return "Apartamento não encontrado no condomínio especificado."