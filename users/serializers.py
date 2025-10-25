from rest_framework import serializers

from core.models import Apartment, Condominium
from .models import Person


class PersonSerializer(serializers.ModelSerializer):


    apartment_number = serializers.IntegerField(write_only=True, required=False)
    apartment_block = serializers.CharField(write_only=True, required=False)
    apartment = serializers.SerializerMethodField()
    condominium = serializers.SlugRelatedField(queryset=Condominium.objects.all(), slug_field='code_condominium')

    managed_condominiums = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Person
        fields = (
            'id', 'name', 'email', 'cpf', 'password', 'telephone', 'user_type', 'apartment_number', 'is_active',
            'apartment_block','apartment', 'position', 'condominium', 'managed_condominiums', 'registered_by'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'registered_by': {'read_only': True},
        }

    def get_apartment(self, obj):
        if obj.apartment:
            from core.serializers import ApartmentSerializer
            return ApartmentSerializer(obj.apartment).data
        return None

    def validate(self, data):
        # Adicione validações personalizadas aqui, se necessário
        user_type = data.get('user_type')
        apartment_number = data.get('apartment_number')
        apartment_block = data.get('apartment_block')
        position = data.get('position')

        if user_type == Person.UserType.RESIDENT:
            if not apartment_number or not apartment_block:
                raise serializers.ValidationError("Moradores devem estar associados a um apartamento.")

        if user_type == Person.UserType.EMPLOYEE and not position:
            raise serializers.ValidationError("Funcionários devem ter um cargo definido.")

        return data

    def create(self, validated_data):
        # Pegando os dados do apartamento
        apartment_number = validated_data.pop('apartment_number', None)
        apartment_block = validated_data.pop('apartment_block', None)

        # Guardando o condomínio antes de criar o usuário
        condominium = validated_data.get('condominium')

        print(f"Número do Apto: {apartment_number}")
        print(f"Bloco do Apto: {apartment_block}")
        print(f"Objeto Condomínio: {condominium}")

        # Criando o usuário
        user = Person.objects.create_user(**validated_data)

        # Associando ao apartamento se os dados foram fornecidos
        if apartment_number and apartment_block and condominium:
            try:
                apt_instance, created = Apartment.objects.get_or_create(
                    number=apartment_number,
                    block=apartment_block,
                    condominium=condominium
                )
                print(f"Apartamento {'criado' if created else 'encontrado'}: {apt_instance}")

                # Atualizando o status do apartamento para 'ocupado' se foi criado agora
                if created:
                    apt_instance.occupation = 'occupied'
                    apt_instance.save()

                user.apartment = apt_instance
                user.save()
                user.refresh_from_db()

            except Apartment.DoesNotExist:
                raise serializers.ValidationError(
                    f"Apartamento não encontrado com número {apartment_number}, bloco {apartment_block} no condomínio especificado.")

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

