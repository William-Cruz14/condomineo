from rest_framework import serializers

from core.filters import getuser
from core.models import Apartment, Condominium
from core.utils import get_user_condo_apartment, get_apartment_number, get_condominium_to_code
from utils.validators import (
    validator_cpf, validator_telephone, validator_email, validator_user_type,
    validate_apartment_and_condominium_fields,
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
                    raise serializers.ValidationError({'recaptcha_token': message})

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
        _, _, apartment = get_user_condo_apartment(self.context, validated_data)

        if apartment and instance.apartment != apartment:
            instance.apartment = apartment

        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

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