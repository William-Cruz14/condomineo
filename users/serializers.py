from rest_framework import serializers
from core.models import Apartment, Condominium
from utils.validators import validator_cpf, validator_telephone, validator_email, validator_user_type
from .models import Person


class PersonSerializer(serializers.ModelSerializer):

    apartment_number = serializers.IntegerField(write_only=True, required=False)
    apartment_block = serializers.CharField(write_only=True, required=False)
    apartment = serializers.SerializerMethodField(read_only=True)
    condominium = serializers.SlugRelatedField(queryset=Condominium.objects.all(), slug_field='code_condominium')

    managed_condominiums = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Person
        fields = (
            'id', 'name', 'email', 'cpf', 'password', 'telephone', 'user_type', 'apartment_number', 'is_active',
            'apartment_block', 'apartment', 'position', 'condominium', 'managed_condominiums', 'registered_by'
        )
        extra_kwargs = {
            'password': {'write_only': True},
        }
        read_only_fields = (
            'id',
            'is_active',
            'registered_by',
        )

    @staticmethod
    def get_apartment(obj):
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

    def create(self, validated_data):
        # Pegando os dados do apartamento
        apartment_number = validated_data.pop('apartment_number', None)
        apartment_block = validated_data.pop('apartment_block', None)

        # Guardando o condomínio antes de criar o usuário
        condominium = validated_data.pop('condominium')

        name = validated_data.pop('name').title()

       # Pegando os dados do apartamento
        if apartment_number and apartment_block and condominium:
            try:
                apartment_block = apartment_block.upper().strip()

                apt_instance, created = Apartment.objects.get_or_create(
                    number=apartment_number,
                    block=apartment_block,
                    condominium=condominium
                )

                # Atualizando a situação do apartamento para 'ocupado' se foi criado agora
                if created:
                    apt_instance.occupation = 'occupied'
                    apt_instance.save()

                person = Person.objects.create_user(
                    apartment=apt_instance,
                    condominium=condominium,
                    name=name,
                    **validated_data
                )
            except Apartment.DoesNotExist:
                raise serializers.ValidationError(
                    f"Apartamento não encontrado com número {apartment_number}, "
                    f"bloco {apartment_block} no condomínio especificado."
                )

        else:
            person = Person.objects.create_user(
                name=name,
                condominium=condominium,
                **validated_data
            )

        return person

    def update(self, instance, validated_data):

        validated_data.pop('apartment_number', None)
        validated_data.pop('apartment_block', None)

        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()

        return instance

