from rest_framework import serializers
from core.utils import get_user_condo_apartment, get_apartment_number, get_condominium_to_code, \
    pop_apartment_and_condominium
from rest_framework.exceptions import ValidationError
from utils.validators import (
    validator_cpf, validator_telephone, validator_email, validator_user_type,
)
from .models import Person


class PersonSerializer(serializers.ModelSerializer):

    number_apartment = serializers.IntegerField(write_only=True, required=False)
    block_apartment = serializers.CharField(write_only=True, required=False)
    apartment = serializers.SerializerMethodField(read_only=True)
    code_condominium = serializers.CharField(write_only=True, required=False)
    recaptcha_token = serializers.CharField(
        write_only=True,
        required=False,
        error_messages={'required': 'O token do reCAPTCHA é obrigatório.'}
    )

    managed_condominiums = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Person
        fields = (
            'id', 'name', 'email', 'cpf', 'password', 'telephone', 'user_type', 'number_apartment', 'is_active',
            'block_apartment', 'apartment', 'position', 'code_condominium', 'managed_condominiums', 'registered_by',
            'recaptcha_token',
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }
        read_only_fields = (
            'id',
            'is_active',
            'registered_by',
        )


    def get_apartment(self, obj):
        """Serializa o apartamento usando importação local para evitar circular import"""
        if obj.apartment:
            from core.serializers import ApartmentSerializer
            return ApartmentSerializer(obj.apartment).data
        return None


    def validate_telephone(self, telephone):
        return validator_telephone(telephone)

    def validate_email(self, email):
        return validator_email(email)

    def validate_cpf(self, cpf):
        return validator_cpf(cpf)

    def validate_user_type(self, user_type):
        return validator_user_type(user_type)


    def validate(self, data):

        is_creating = self.instance is None
        if is_creating:
            token = data.pop('recaptcha_token')
            
            if token:
                from users.services import verificar_recaptcha
                success, message = verificar_recaptcha(token)
                if not success:
                    raise ValidationError({'recaptcha_token': message})

        if self.context['request'].method == 'POST':
            # Verifica se o código do condomínio foi fornecido para moradores e funcionários
            if not data.get('code_condominium'):
                raise ValidationError("code_condominium: Código do condomínio é obrigatório para moradores e funcionários.")

            # Validações específicas para moradores
            if data.get('user_type') == Person.UserType.RESIDENT:
                if not data.get('number_apartment') or not data.get('block_apartment'):
                    raise ValidationError(
                        "number_apartment / block_apartment: Número e bloco do apartamento são obrigatórios para moradores."
                    )

                if data.get('code_condominium') and (data.get('number_apartment') and data.get('block_apartment')):
                    apartment = get_apartment_number(
                        get_condominium_to_code(data.get('code_condominium')),
                        data.get('number_apartment'),
                        data.get('block_apartment')
                    )
                    if apartment:
                        if hasattr(apartment, 'main_resident') and apartment.main_resident:
                            raise ValidationError("Apartamento já possui um morador principal associado.")
                    else:
                        raise ValidationError("Apartamento não encontrado para os dados fornecidos.")

            # Validações específicas para funcionários
            elif data.get('user_type') == Person.UserType.EMPLOYEE:
                    if not data.get('position'):
                        raise ValidationError(
                            "position: Cargo são obrigatórios para funcionários."
                        )

        return super().validate(data)


    def create(self, validated_data):
        _, condo, apartment = get_user_condo_apartment(self.context, validated_data)

        validated_data['name'] = validated_data['name'].title()

        if apartment:
            # Atualiza a situação do apartamento para 'ocupado' se foi criado agora
            if apartment.occupation != 'occupied':
                apartment.occupation = 'occupied'
                apartment.save()

            person = Person.objects.create_user(
                apartment=apartment,
                condominium=condo,
                **validated_data
            )
        else:
            person = Person.objects.create_user(
                condominium=condo,
                **validated_data
            )

        return person

    def update(self, instance, validated_data):
        condo, number, block = pop_apartment_and_condominium(validated_data)

        if number and block and condo :
            condominium = get_condominium_to_code(condo)
            apartment = get_apartment_number(condominium, number, block)

            if apartment and instance.apartment != apartment:
                instance.apartment = apartment

        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        if 'name' in validated_data:
            validated_data['name'] = validated_data['name'].title()

        return super().update(instance, validated_data)



class CustomUserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para a resposta de login.
    """
    is_new_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Person
        fields = ('id', 'email', 'name', 'is_new_user')
        read_only_fields = ('id', 'email', 'name', 'is_new_user')

    def get_is_new_user(self, obj):
        # 'obj' é a instância do usuário (Person)
        # Se o CPF estiver em branco, é um usuário novo/incompleto.
        if not obj.cpf:
            return True
        return False