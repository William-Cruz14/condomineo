from rest_framework import serializers

def validator_cpf(value):
    """
    Validando o número do CPF.
    """
    if len(value) != 11 or value == value[0] * 11:
        raise serializers.ValidationError("Número de CPF inválido.")

    if not value.isdigit():
        raise serializers.ValidationError("Número de CPF deve conter apenas dígitos.")

    return value


def validator_telephone(value):
    """
    Validando o número de telefone.
    """

    if len(value) not in [10, 11]:
        raise serializers.ValidationError("Número de telefone inválido. Deve conter 10 ou 11 dígitos.")

    if not value.isdigit():
        raise serializers.ValidationError("Número de telefone deve conter apenas dígitos.")

    return value


def validator_email(value):
    """
    Validando o formato do e-mail.
    """

    if "@" not in value or "." not in value.split("@")[-1]:
        raise serializers.ValidationError("Formato de e-mail inválido.")

    return value


def validator_user_type(value):
    """
    Validando o tipo de usuário.
    """

    valid_types = ['resident', 'employee', 'admin']
    if value not in valid_types:
        raise serializers.ValidationError(f"Tipo de usuário inválido. Deve ser um dos seguintes: {', '.join(valid_types)}.")

    return value

def validator_value_finance(value):
    """
    Validando o valor financeiro.
    """
    if value < 0:
        raise serializers.ValidationError("O valor financeiro não pode ser negativo.")

    return value


def validate_apartment_and_condominium_fields(user, data):
    """
    Valida campos obrigatórios de apartamento e condomínio baseado no tipo de usuário.
    """
    if user.user_type == "employee":
        if not data.get('apartment_number') or not data.get('apartment_block'):
            raise serializers.ValidationError(
                "Para funcionários os campos 'apartment_number' e "
                "'apartment_block' são obrigatórios."
            )

    if user.user_type == "admin":
        if not data.get("code_condominium") and not data.get("apartment_number") and not data.get("apartment_block"):
            raise serializers.ValidationError(
                "Para administradores, o campo 'code_condominium' é obrigatório."
            )