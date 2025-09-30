from rest_framework import serializers

from core.models import Apartment, Condominium
from .models import Person
from core.serializers import ApartmentSerializer


class PersonSerializer(serializers.ModelSerializer):

    apartment = serializers.PrimaryKeyRelatedField(queryset=Apartment.objects.all(), required=False)
    condominium = serializers.SlugRelatedField(queryset=Condominium.objects.all(), slug_field='code_condominium')
    apartment_detail = ApartmentSerializer(source='apartment', read_only=True)

    managed_condominiums = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Person
        fields = (
            'id', 'name', 'email', 'cpf', 'password', 'telephone', 'user_type', 'apartment',
            'apartment_detail', 'position', 'condominium', 'managed_condominiums', 'registered_by'
        )
        extra_kwargs = {'password': {'write_only': True}}


    def validate(self, data):
        # Adicione validações personalizadas aqui, se necessário
        user_type = data.get('user_type')
        apartment = data.get('apartment')
        position = data.get('position')

        if user_type == Person.UserType.RESIDENT and not apartment:
            raise serializers.ValidationError("Moradores devem estar associados a um apartamento.")

        if user_type == Person.UserType.EMPLOYEE and not position:
            raise serializers.ValidationError("Funcionários devem ter um cargo definido.")

        return data

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Person(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

