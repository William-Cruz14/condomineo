from rest_framework import serializers
from users.serializers import PersonSerializer
from .models import Visitor, Reservation, Apartment, Finance, Vehicle, Order, Visit, Condominium, Address, Resident


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CondominiumSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    class Meta:
        model = Condominium
        fields = (
            'id', 'name', 'address', 'cnpj',
            'code_condominium', 'created_at', 'created_by'
        )

        extra_kwargs = {
            'code_condominium': {'read_only': True},
            'created_at': {'read_only': True},
            'created_by': {'read_only': True},
        }

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        address = Address.objects.create(**address_data)
        condominium = Condominium.objects.create(address=address, **validated_data)
        return condominium


class VisitorSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    code_condominium = serializers.CharField(write_only=True)
    registered_by = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)

    class Meta:
        model = Visitor
        fields = (
            'id', 'name', 'cpf', 'telephone',
            'registered_by', 'condominium', 'code_condominium'
        )
        read_only_fields = (
            'id',
            'registered_by',
            'condominium',
        )

    def create(self, validated_data):
        # Extrai o código do condomínio dos dados validados
        code_condominium = validated_data.pop('code_condominium')
        # Busca o condomínio correspondente ao código fornecido
        condominium = Condominium.objects.get(code_condominium=code_condominium)
        # Cria a instância de Visitor associada ao condomínio encontrado
        visitor = Visitor.objects.create(condominium=condominium, **validated_data)
        return visitor


class ReservationSerializer(serializers.ModelSerializer):

    # O campo 'resident' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    resident = PersonSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = (
            'id', 'resident', 'space',
            'start_time', 'end_time'
        )
        read_only_fields = (
            'id',
            'resident'
        )

class ReservationAdminSerializer(serializers.ModelSerializer):

    resident = PersonSerializer(read_only=True)
    apartment_code = serializers.CharField(write_only=True)
    apartment_block = serializers.CharField(write_only=True)

    class Meta:
        model = Reservation
        fields = (
            'id', 'resident', 'space',
            'start_time', 'end_time', 'apartment_code', 'apartment_block'
        )
        read_only_fields = (
            'id',
            'resident'
        )

    def create(self, validated_data):
        # Extrai o número e bloco do apartamento dos dados validados
        number_apartment = validated_data.pop('apartment_code')
        block_apartment = validated_data.pop('apartment_block')
        # Buscar o apartamento com base no número e bloco fornecidos
        apartment = Apartment.objects.get(number=number_apartment, block=block_apartment)
        # Obter o residente principal do apartamento para definir como quem fez a reserva
        main_resident = apartment.main_residents.first()
        # Cria a instância de Reservation associada ao residente principal encontrado
        reservation = Reservation.objects.create(
            resident=main_resident,
            **validated_data
        )
        return reservation


class FinanceSerializer(serializers.ModelSerializer):
    creator = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    condominium_code = serializers.CharField(write_only=True)

    class Meta:
        model = Finance
        fields = (
            'id', 'creator', 'value', 'date', 'description',
            'document', 'condominium', 'condominium_code'
        )
        read_only_fields = (
            'id', 'creator', 'condominium'
        )

    def create(self, validated_data):
        # Extrai o código do condomínio dos dados validados
        code_condominium = validated_data.pop('condominium_code')
        # Busca o condomínio correspondente ao código fornecido
        condominium = Condominium.objects.get(code_condominium=code_condominium)
        # Cria a instância de Finance associada ao condomínio encontrado
        finance = Finance.objects.create(condominium=condominium, **validated_data)
        return finance

class ApartmentSerializer(serializers.ModelSerializer):
    condominium = serializers.SlugRelatedField(queryset=Condominium.objects.all(), slug_field='code_condominium')
    condominium_detail = CondominiumSerializer(source='condominium', read_only=True)

    class Meta:
        model = Apartment
        fields = (
            'id', 'number', 'block', 'tread', 'occupation',
            'entry_date', 'exit_date', 'condominium', 'condominium_detail'
        )


class ResidentSerializer(serializers.ModelSerializer):
    apartment_details = ApartmentSerializer(read_only=True)
    registered_by = PersonSerializer(read_only=True)

    class Meta:
        model = Resident
        fields = (
            'id',
            'name',
            'cpf',
            'phone',
            'registered_by',
            'apartment',
            'apartment_details',
            'created_at',
        )
        read_only_fields = (
            'id',
            'registered_by',
            'apartment',
            'apartment_details',
            'created_at'
        )

    def validate(self, data):
        # Validação personalizada para o campo CPF
        if not data.get('cpf').isdigit():
            raise serializers.ValidationError('CPF deve conter apenas números.')
        if len(data['cpf']) != 11:
            raise serializers.ValidationError('CPF deve ter exatamente 11 dígitos.')
        return data

class ResidentAdminSerializer(serializers.ModelSerializer):
    apartment_number = serializers.IntegerField(write_only=True)
    apartment_block = serializers.CharField(write_only=True)
    apartment_details = ApartmentSerializer(read_only=True)
    registered_by = PersonSerializer(read_only=True)
    class Meta:
        model = Resident
        fields = (
            'id',
            'name',
            'cpf',
            'phone',
            'registered_by',
            'apartment',
            'apartment_number',
            'apartment_block',
            'apartment_details',
            'created_at',
        )
        read_only_fields = (
            'id',
            'registered_by',
            'apartment',
            'apartment_details',
            'created_at'
        )

    def create(self, validated_data):
        # Extrair o número e bloco do apartamento dos dados validados
        number_apartment = validated_data.pop('apartment_number')
        block_apartment = validated_data.pop('apartment_block')
        # Buscar o apartamento com base no número e bloco fornecidos
        apartment, _ = Apartment.objects.get_or_create(number=number_apartment, block=block_apartment)
        # Obter o residente principal do apartamento para definir como quem registrou o novo residente
        main_resident = apartment.main_residents.first()
        # Criar o residente associando-o ao apartamento e ao residente principal
        resident = Resident.objects.create(
            apartment=apartment,
            registered_by=main_resident,
            **validated_data
        )
        return resident

class VisitSerializer(serializers.ModelSerializer):
    # O campo 'visitor' é um campo de chave estrangeira que permite selecionar um visitante
    visitor = VisitorSerializer(read_only=True)
    # O campo 'apartment' é um campo de chave estrangeira que permite selecionar um apartamento
    apartment = ApartmentSerializer(read_only=True)
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = PersonSerializer(read_only=True)

    name_visitor = serializers.CharField(write_only=True)
    cpf_visitor = serializers.CharField(write_only=True)
    apartment_number = serializers.IntegerField(write_only=True)
    apartment_block = serializers.CharField(write_only=True)

    class Meta:
        model = Visit
        fields = (
            'id', 'visitor', 'apartment', 'entry_date',
            'observation','exit_date', 'registered_by', 'name_visitor',
            'cpf_visitor', 'apartment_number', 'apartment_block'
        )
        read_only_fields = (
            'id',
            'visitor',
            'apartment',
            'registered_by',

        )

    def create(self, validated_data):
        # Extrair os dados do visitante e do apartamento dos dados validados
        name_visitor = validated_data.pop('name_visitor')
        cpf_visitor = validated_data.pop('cpf_visitor')
        number_apartment = validated_data.pop('apartment_number')
        block_apartment = validated_data.pop('apartment_block')

        # Buscar o apartamento com base no número e bloco fornecidos
        apartment = Apartment.objects.get(number=number_apartment, block=block_apartment)

        # Buscar ou criar o visitante com base no nome e CPF fornecidos
        visitor, _ = Visitor.objects.get_or_create(
            name=name_visitor,
            cpf=cpf_visitor,
            condominium=apartment.condominium
        )

        # Criar a visita associando-a ao visitante e ao apartamento encontrados
        visit = Visit.objects.create(
            visitor=visitor,
            apartment=apartment,
            **validated_data
        )
        return visit


class VehicleSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    apartment_number = serializers.IntegerField(write_only=True)
    apartment_block = serializers.CharField(write_only=True)
    condominium = CondominiumSerializer(read_only=True)
    owner = PersonSerializer(read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'id', 'registered_by', 'plate',
            'model', 'color', 'owner', 'condominium',
            'condominium_id', 'apartment_number', 'apartment_block'
        )
        read_only_fields = (
            'id',
            'registered_by',
            'owner',
            'condominium',
        )

    def create(self, validated_data):
        # Extrair o número e bloco do apartamento dos dados validados
        number_apartment = validated_data.pop('apartment_number')
        block_apartment = validated_data.pop('apartment_block')

        # Buscar o apartamento com base no número e bloco fornecidos
        apartment = Apartment.objects.get(number=number_apartment, block=block_apartment)
        # Obter o residente principal do apartamento para definir como proprietário do veículo
        main_resident = apartment.main_residents.first()
        # Criar o veículo associando-o ao residente principal e ao condomínio do apartamento
        vehicle = Vehicle.objects.create(
            owner=main_resident,
            condominium=apartment.condominium,
            **validated_data
        )
        return vehicle


class OrderSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = PersonSerializer(read_only=True)
    apartment_number = serializers.IntegerField(write_only=True)
    apartment_block = serializers.CharField(write_only=True)
    owner = PersonSerializer(read_only=True)
    class Meta:
        model = Order
        fields = (
            'id', 'order_code', 'status',
            'signature_image', 'registered_by', 'owner', 'apartment_number', 'apartment_block'
        )
        read_only_fields = ('id', 'owner', 'registered_by')

    def create(self, validated_data):
        # Extrair o número e bloco do apartamento dos dados validados
        number_apartment = validated_data.pop('apartment_number')
        block_apartment = validated_data.pop('apartment_block')

        # Buscar o apartamento com base no número e bloco fornecidos
        apartment = Apartment.objects.get(number=number_apartment, block=block_apartment)
        # Obter o residente principal do apartamento para definir como proprietário do pedido
        main_resident = apartment.main_residents.first()
        # Criar o pedido associando-o ao residente principal
        order = Order.objects.create(
            owner=main_resident,
            **validated_data
        )
        return order