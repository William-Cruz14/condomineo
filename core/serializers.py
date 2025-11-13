from rest_framework import serializers
from users.serializers import PersonSerializer
from .filters import getuser
from core.models import (
    Visitor, Reservation, Apartment, Finance,
    Vehicle, Order, Visit, Condominium, Address, Resident,
    Notice, Communication, Occurrence
)
from users.models import Person
from .utils import get_condominium_to_code, get_apartment_number, get_user_condo_apartment
from utils.validators import validator_cpf, validator_telephone, validator_email, \
    validate_apartment_and_condominium_fields, validator_value_finance


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CondominiumSerializer(serializers.ModelSerializer):
    address_street = serializers.CharField(write_only=True)
    address_complement = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address_neighborhood = serializers.CharField(write_only=True, required=False, allow_blank=True)
    address_city = serializers.CharField(write_only=True)
    address_state = serializers.CharField(write_only=True)
    address_zip_code = serializers.CharField(write_only=True)
    address_number = serializers.IntegerField(write_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Condominium
        fields = (
            'id', 'name', 'address', 'cnpj', 'created_at', 'created_by',
            'address_street', 'address_complement', 'address_neighborhood',
            'address_city', 'address_state', 'address_zip_code', 'address_number',
            'code_condominium'
        )

        read_only_fields = (
            'id',
            'created_at',
            'created_by',
            'code_condominium'
        )

    def create(self, validated_data):
        # Pega o usuário autenticado
        user = self.context['request'].user

        # Extrai os dados do endereço dos dados validados
        address_street = validated_data.pop('address_street')
        address_number = validated_data.pop('address_number')
        address_complement = validated_data.pop('address_complement', '')
        address_neighborhood = validated_data.pop('address_neighborhood', '')
        address_city = validated_data.pop('address_city')
        address_state = validated_data.pop('address_state')
        address_zip_code = validated_data.pop('address_zip_code')


        address = Address.objects.create(
            street=address_street,
            number=address_number,
            complement=address_complement,
            neighborhood=address_neighborhood,
            city=address_city,
            state=address_state,
            zip_code=address_zip_code
        )
        condominium = Condominium.objects.create(
            address=address,
            created_by=user,
            **validated_data
        )

        user.managed_condominiums.add(condominium)
        return condominium

    def update(self, instance, validated_data):
        address_data = {
            'street': validated_data.pop('address_street', instance.address.street),
            'number': validated_data.pop('address_number', instance.address.number),
            'complement': validated_data.pop('address_complement', instance.address.complement),
            'neighborhood': validated_data.pop('address_neighborhood', instance.address.neighborhood),
            'city': validated_data.pop('address_city', instance.address.city),
            'state': validated_data.pop('address_state', instance.address.state),
            'zip_code': validated_data.pop('address_zip_code', instance.address.zip_code),
        }

        address = instance.address

        for attr, value in address_data.items():
            setattr(address, attr, value)
        address.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

class ApartmentSerializer(serializers.ModelSerializer):
    condominium = serializers.SlugRelatedField(queryset=Condominium.objects.all(), slug_field='code_condominium')
    condominium_detail = CondominiumSerializer(source='condominium', read_only=True)

    class Meta:
        model = Apartment
        fields = (
            'id', 'number', 'block', 'tread', 'occupation',
            'entry_date', 'exit_date', 'condominium', 'condominium_detail'
        )
        read_only_fields = (
            'id',
            'entry_date',
            'condominium_detail'
        )

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

    def validate(self, data):
        user = getuser(self.context['request'])

        if not self.instance:
            # Ao criar, todos os campos são obrigatórios
            validate_apartment_and_condominium_fields(user, data)

        return data

    def validate_cpf(self, cpf):
        validator_cpf(cpf)
        return cpf

    def validate_telephone(self, telephone):
        validator_telephone(telephone)
        return telephone

    def create(self, validated_data):
        user, condo, _ = get_user_condo_apartment(self.context, validated_data)
        # Formata o nome do visitante
        validated_data['name'] = validated_data['name'].title()

        # Cria a instância de Visitor associada ao condomínio encontrado
        visitor = Visitor.objects.get_or_create(
            condominium=condo,
            registered_by=user,
            **validated_data
        )

        return visitor

    def update(self, instance, validated_data):
        # Atualiza os campos do visitante
        cpf = validated_data.get('cpf')
        if cpf:
            instance.cpf = cpf

        telephone = validated_data.get('telephone')
        if telephone:
            instance.telephone = telephone

        name = validated_data.get('name')
        if name:
            instance.name = name.title()


        return super().update(instance, validated_data)

class VisitSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = PersonSerializer(read_only=True)
    visitor = VisitorSerializer(read_only=True)
    apartment = ApartmentSerializer(read_only=True)

    # Campos adicionais para receber o apartamento e condomínio
    code_condominium = serializers.CharField(write_only=True)
    number_apartment = serializers.IntegerField(write_only=True)
    block_apartment = serializers.CharField(write_only=True)

    # Campos adicionais para receber o nome e CPF do visitante
    name_visitor = serializers.CharField(write_only=True)
    cpf_visitor = serializers.CharField(write_only=True)

    class Meta:
        model = Visit
        fields = (
            'id','condominium', 'visitor', 'apartment', 'entry_date',
            'observation','exit_date', 'registered_by', 'name_visitor', 'cpf_visitor',
            'number_apartment', 'block_apartment', 'code_condominium'
        )
        read_only_fields = (
            'id',
            'condominium',
            'visitor',
            'apartment',
            'entry_date',
            'registered_by',

        )

    def validate(self, data):
        user = getuser(self.context['request'])
        if not self.instance:
            validate_apartment_and_condominium_fields(user, data)

        return data

    def validate_cpf(self, cpf):
        validator_cpf(cpf)
        return cpf

    def create(self, validated_data):
        user, condo, apartment = get_user_condo_apartment(self.context, validated_data)

        # Buscar ou criar o visitante com base no nome,CPF e condomínio fornecidos
        name_visitor = validated_data.pop('name_visitor')
        cpf_visitor = validated_data.pop('cpf_visitor')

        visitor, _ = Visitor.objects.get_or_create(
            name=name_visitor.title(),
            cpf=cpf_visitor,
            registered_by=user,
            condominium=condo
        )

        # Criar a visita associando-a ao visitante encontrado
        visit = Visit.objects.create(
            condominium=condo,
            apartment=apartment,
            visitor=visitor,
            registered_by=user,
            **validated_data
        )
        return visit

    def update(self, instance, validated_data):
        user, _, apartment = get_user_condo_apartment(self.context, validated_data)

        name_visitor = validated_data.pop('name_visitor', None)
        cpf_visitor = validated_data.pop('cpf_visitor', None)

        if apartment:
            if user.apartment != apartment:
                instance.apartment = apartment

        if name_visitor and cpf_visitor:
            visitor, _ = Visitor.objects.get_or_create(
                condominium=instance.condominium,
                name=name_visitor.title(),
                cpf=cpf_visitor,
                registered_by=instance.registered_by
            )
            instance.visitor = visitor

        return super().update(instance, validated_data)

class ReservationSerializer(serializers.ModelSerializer):

    # O campo 'resident' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    resident = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)

    code_condominium = serializers.CharField(write_only=True, required=False)
    apartment_number = serializers.CharField(write_only=True, required=False)
    apartment_block = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Reservation
        fields = (
            'id', 'resident', 'space', 'start_time', 'end_time',
            'condominium', 'code_condominium', 'apartment_number', 'apartment_block'
        )
        read_only_fields = ('id', 'resident', 'condominium')


    def validate(self, data):
        user = getuser(self.context['request'])
        if not self.instance:
            validate_apartment_and_condominium_fields(user, data)

        return data

    def create(self, validated_data):
        user, condo, apartment = get_user_condo_apartment(self.context, validated_data)

        # Criar a instância de Reservation associada ao residente encontrado
        reservation = Reservation.objects.create(
            resident=apartment.main_residents.first(),
            condominium=condo,
            **validated_data
        )

        return reservation

    def update(self, instance, validated_data):
        user, _, apartment = get_user_condo_apartment(self.context, validated_data)

        if apartment:
            if user.apartment != apartment:
                instance.resident = apartment.main_residents.first()


        return super().update(instance, validated_data)

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

    def validate_value(self, value):
        validator_value_finance(value)
        return value

    def create(self, validated_data):
        user , condo, _ = get_user_condo_apartment(self.context, validated_data)

        # Cria a instância de Finance associada ao condomínio encontrado
        finance = Finance.objects.create(
            creator=user,
            condominium=condo,
            **validated_data
        )
        return finance

    def update(self, instance, validated_data):
        # Aqui estou tratando a possível atualização do condomínio
        code_condominium = validated_data.pop('condominium_code', None)
        # Se um novo código de condomínio for fornecido, atualize o condomínio associado
        if code_condominium:
            condominium = get_condominium_to_code(code_condominium)
            instance.condominium = condominium

        return super().update(instance, validated_data)

class ResidentSerializer(serializers.ModelSerializer):
    apartment = ApartmentSerializer(read_only=True)
    registered_by = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)

    # Campos opcionais para administradores/funcionários
    code_condominium = serializers.CharField(write_only=True, required=False)
    apartment_number = serializers.IntegerField(write_only=True, required=False)
    apartment_block = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Resident
        fields = (
            'id', 'name', 'cpf', 'email', 'phone',
            'condominium', 'apartment',
            'registered_by', 'created_at',
            'code_condominium', 'apartment_number', 'apartment_block'
        )
        read_only_fields = (
            'id', 'registered_by', 'apartment',
            'created_at', 'condominium'
        )

    def validate(self, data):
        user = self.context['request'].user
        # Se não for residente, exige dados do apartamento
        if not self.instance:
            validate_apartment_and_condominium_fields(user, data)
        return data

    def validate_cpf(self, value):
        validator_cpf(value)
        return value

    def validate_email(self, value):
        validator_email(value)
        return value

    def validate_phone(self, value):
        validator_telephone(value)
        return value

    def create(self, validated_data):
        user, condo, apartment = get_user_condo_apartment(self.context, validated_data)

        # Criar residente
        resident = Resident.objects.create(
            condominium=condo,
            apartment=apartment,
            registered_by=user,
            **validated_data
        )
        return resident

    def update(self, instance, validated_data):
        # Atualiza os campos do residente
        user, _, apartment = get_user_condo_apartment(self.context, validated_data)
        if apartment:
            if user.apartment != apartment:
                instance.apartment = apartment

        cpf = validated_data.get('cpf')
        if cpf:
            instance.cpf = cpf

        email = validated_data.get('email')
        if email:
            instance.email = email

        name = validated_data.get('name')
        if name:
            instance.name = name.title()

        phone = validated_data.get('phone')
        if phone:
            instance.phone = phone

        return super().update(instance, validated_data)

class VehicleSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    apartment_number = serializers.IntegerField(write_only=True)
    apartment_block = serializers.CharField(write_only=True)
    code_condominium = serializers.CharField(write_only=True)
    condominium = CondominiumSerializer(read_only=True)
    owner = PersonSerializer(read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'id', 'registered_by', 'plate',
            'model', 'color', 'owner', 'condominium',
            'code_condominium', 'apartment_number', 'apartment_block'
        )
        read_only_fields = (
            'id',
            'registered_by',
            'owner',
            'condominium',
        )

    def validate(self, data):
        user = self.context['request'].user
        # Se não for residente, exige dados do apartamento
        if not self.instance:
            validate_apartment_and_condominium_fields(user, data)
        return data


    def create(self, validated_data):
        user, condo, apartment = get_user_condo_apartment(self.context, validated_data)

        #Criar o veículo associando-o ao residente principal e ao responsável pelo registro
        vehicle = Vehicle.objects.create(
            condominium=condo,
            registered_by=user,
            owner=apartment.main_residents.first(),
            **validated_data
        )
        return vehicle

    def update(self, instance, validated_data):
        user, _, apartment = get_user_condo_apartment(self.context, validated_data)

        if apartment:
            if user.apartment != apartment:
                instance.owner = apartment.main_residents.first()


        return super().update(instance, validated_data)

class OccurrenceSerializer(serializers.ModelSerializer):

    condominium = CondominiumSerializer(read_only=True)
    apartment_number = serializers.IntegerField(write_only=True)
    apartment_block = serializers.CharField(write_only=True)
    code_condominium = serializers.CharField(write_only=True)
    reported_by = PersonSerializer(read_only=True)

    class Meta:
        model = Occurrence
        fields = (
            'id', 'title', 'description', 'status',
            'date_reported', 'condominium', 'reported_by',
            'apartment_number', 'apartment_block', 'code_condominium'
        )
        read_only_fields = ('id', 'date_reported', 'condominium')

    def validate(self, data):
        user = self.context['request'].user
        # Se não for residente, exige dados do apartamento
        if not self.instance:
            validate_apartment_and_condominium_fields(user, data)
        return data

    def create(self, validated_data):

        title = validated_data.pop('title', None)
        status = validated_data.pop('status', None)

        # Busca o condomínio correspondente ao código fornecido
        user, condo, apartment = get_user_condo_apartment(self.context, validated_data)

        occurrence = Occurrence.objects.create(
            condominium=condo,
            reported_by=apartment.main_residents.first(),
            title=title.title(),
            status=status.lower(),
            **validated_data
        )
        return occurrence


    def update(self, instance, validated_data):

        user, _, apartment = get_user_condo_apartment(self.context, validated_data)
        if apartment:
            if user.apartment != apartment:
                instance.reported_by = apartment.main_residents.first()

        return super().update(instance, validated_data)

class OrderSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    owner = PersonSerializer(read_only=True)

    apartment_number = serializers.IntegerField(write_only=True, required=False)
    apartment_block = serializers.CharField(write_only=True, required=False)
    code_condominium = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = (
            'id', 'order_code', 'status', 'code_condominium', 'condominium',
            'signature_image', 'registered_by', 'owner', 'apartment_number', 'apartment_block'
        )
        read_only_fields = ('id', 'owner', 'registered_by', 'condominium')

    def validate(self, data):
        user = self.context['request'].user
        # Se não for residente, exige dados do apartamento
        if not self.instance:
            validate_apartment_and_condominium_fields(user, data)
        return data

    def create(self, validated_data):
        # Pega o usuário autenticado
        user, condo, apartment = get_user_condo_apartment(self.context, validated_data)

        # Criar o pedido associando-o ao residente principal
        order = Order.objects.create(
            condominium=condo,
            owner=apartment.main_residents.first(),
            registered_by=user,
            **validated_data
        )
        return order

    def update(self, instance, validated_data):
        user, _, apartment = get_user_condo_apartment(self.context, validated_data)

        if apartment:
            if user.apartment != apartment:
                instance.owner = apartment.main_residents.first()

        return super().update(instance, validated_data)

class NoticeSerializer(serializers.ModelSerializer):
    author = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    code_condominium = serializers.CharField(write_only=True)

    class Meta:
        model = Notice
        fields = (
            'id', 'title', 'content', 'created_at', 'file_complement',
            'author', 'condominium', 'code_condominium'
        )
        read_only_fields = (
            'id', 'created_at', 'author', 'condominium'
        )

    def create(self, validated_data):

        user , condo, _ = get_user_condo_apartment(self.context, validated_data)

        validated_data['title'] = validated_data['title'].title()

        # Cria a instância de Notice associada ao condomínio encontrado
        notice = Notice.objects.create(
            condominium=condo,
            author=user,
            **validated_data
        )
        return notice

    def update(self, instance, validated_data):
        title = validated_data.get('title')
        if title:
            instance.title = title.title()

        return super().update(instance, validated_data)


class CommunicationSerializer(serializers.ModelSerializer):
    sender = PersonSerializer(read_only=True)
    recipients = PersonSerializer(many=True, read_only=True)
    condominium = CondominiumSerializer(read_only=True)

    # Campos para administradores/funcionários enviarem para apartamentos
    code_condominium = serializers.CharField(write_only=True, required=False)
    apartment_number = serializers.IntegerField(write_only=True, required=False)
    apartment_block = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Communication
        fields = (
            'id', 'title', 'message', 'created_at', 'apartment_number', 'apartment_block',
            'sender', 'recipients', 'condominium', 'code_condominium', 'communication_type'
        )
        read_only_fields = (
            'id', 'created_at', 'sender', 'recipients', 'condominium'
        )

    def validate(self, data):
        user = self.context['request'].user
        # Se não for residente, exige dados do apartamento
        if not self.instance:
            validate_apartment_and_condominium_fields(user, data)
        return data

    def create(self, validated_data):
        user = getuser(self.context['request'])

        code_condominium = validated_data.pop('code_condominium', None)
        apartment_number = validated_data.pop('apartment_number', None)
        apartment_block = validated_data.pop('apartment_block', None)

        # Determina o condomínio
        if code_condominium:
            condominium = get_condominium_to_code(code_condominium)
        else:
            condominium = user.condominium

        # Determina os destinatários com base no tipo de usuário e nos dados fornecidos
        if user.user_type == 'resident':
            if apartment_number and apartment_block:
                # Morador envia para outro apartamento
                apartment = get_apartment_number(
                    condominium,
                    apartment_number,
                    apartment_block
                )
                recipients_qs = apartment.main_residents.all()
            else:
                # Morador envia para a administração
                admins = Person.objects.filter(
                    user_type='admin',
                    managed_condominiums=condominium
                )
                employees = Person.objects.filter(
                    user_type='employee',
                    condominium=condominium
                )
                recipients_qs = admins.union(employees)
        else:
            # Admin/Funcionário envia para um apartamento
            apartment = get_apartment_number(
                condominium,
                apartment_number,
                apartment_block
            )
            recipients_qs = apartment.main_residents.all()

        communication = Communication.objects.create(
            condominium=condominium,
            sender=user,
            **validated_data
        )
        communication.recipients.set(recipients_qs)

        return communication

    def update(self, instance, validated_data):
        code_condominium = validated_data.pop('code_condominium', None)
        apartment_number = validated_data.pop('apartment_number', None)
        apartment_block = validated_data.pop('apartment_block', None)

        if code_condominium:
            condominium = get_condominium_to_code(code_condominium)
            instance.condominium = condominium

        if apartment_number and apartment_block:
            apartment = get_apartment_number(
                instance.condominium,
                apartment_number,
                apartment_block
            )
            recipients_qs = apartment.main_residents.all()
            instance.recipients.set(recipients_qs)

        title = validated_data.pop('title')
        if title:
            instance.title = title.title()

        message = validated_data.pop('message')
        if message:
            instance.message = message

        return super().update(instance, validated_data)

