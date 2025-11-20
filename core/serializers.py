from rest_framework import serializers
from users.serializers import PersonSerializer
from .filters import getuser
from core.models import (
    Visitor, Reservation, Apartment, Finance,
    Vehicle, Order, Visit, Condominium, Address, Resident,
    Notice, Communication, Occurrence
)
from users.models import Person
from .utils import get_condominium_to_code, get_user_condo_apartment
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
        name = validated_data.get('name')
        validated_data['name'] = name.title()

        user, condo, _ = get_user_condo_apartment(self.context, validated_data)

        # Cria a instância de Visitor associada ao condomínio encontrado
        visitor, _ = Visitor.objects.get_or_create(
            condominium=condo,
            registered_by=user,
            **validated_data
        )

        return visitor

    def update(self, instance, validated_data):
        # Atualiza os campos do visitante
        cpf = validated_data.get('cpf')
        if cpf:
            validated_data['cpf'] = cpf

        telephone = validated_data.get('telephone')
        if telephone:
            validated_data['telephone'] = telephone

        name = validated_data.get('name')
        if name:
            validated_data['name'] = name.title()


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
    number_apartment = serializers.IntegerField(write_only=True, required=False)
    block_apartment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Reservation
        fields = (
            'id', 'resident', 'space', 'start_time', 'end_time',
            'condominium', 'code_condominium', 'number_apartment', 'block_apartment'
        )
        read_only_fields = ('id', 'resident', 'condominium')


    def validate(self, data):
        user = getuser(self.context['request'])
        if not self.instance:
            validate_apartment_and_condominium_fields(user, data)

            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError('A hora de início deve ser anterior à hora de término.')

            if Reservation.objects.filter(
                condominium__code_condominium=data['code_condominium'],
                space=data['space'],
                start_time__lt=data['end_time'],
                end_time__gt=data['start_time']
            ).exists():
                raise serializers.ValidationError('Já existe uma reserva para este espaço no período selecionado.')

        return data

    def create(self, validated_data):
        user, condo, apartment = get_user_condo_apartment(self.context, validated_data)

        # Criar a instância de Reservation associada ao residente encontrado
        reservation = Reservation.objects.create(
            resident=apartment.main_resident,
            condominium=condo,
            **validated_data
        )

        return reservation

    def update(self, instance, validated_data):
        user, _, apartment = get_user_condo_apartment(self.context, validated_data)

        if apartment:
            if user.apartment != apartment:
                instance.resident = apartment.main_resident


        return super().update(instance, validated_data)

class FinanceSerializer(serializers.ModelSerializer):
    creator = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    code_condominium = serializers.CharField(write_only=True)
    value = serializers.FloatField()

    class Meta:
        model = Finance
        fields = (
            'id', 'creator', 'value', 'date', 'description',
            'document', 'condominium', 'code_condominium'
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
    number_apartment = serializers.IntegerField(write_only=True, required=False)
    block_apartment = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Resident
        fields = (
            'id', 'name', 'cpf', 'email', 'phone',
            'condominium', 'apartment',
            'registered_by', 'created_at',
            'code_condominium', 'number_apartment', 'block_apartment'
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

        name = validated_data.get('name')
        if name:
            validated_data['name'] = name.title()

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

        name = validated_data.get('name')
        if name:
            validated_data['name'] = name.title()

        return super().update(instance, validated_data)

class VehicleSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    number_apartment = serializers.IntegerField(write_only=True)
    block_apartment = serializers.CharField(write_only=True)
    code_condominium = serializers.CharField(write_only=True)
    condominium = CondominiumSerializer(read_only=True)
    owner = PersonSerializer(read_only=True)

    class Meta:
        model = Vehicle
        fields = (
            'id', 'registered_by', 'plate',
            'model', 'color', 'owner', 'condominium',
            'code_condominium', 'number_apartment', 'block_apartment'
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

        plate = validated_data.get('plate')
        color = validated_data.get('color')
        model = validated_data.get('model')

        if model:
            validated_data['model'] = model.title()

        if plate:
            validated_data['plate'] = plate.upper()

        if color:
            validated_data['color'] = color.title()

        #Criar o veículo associando-o ao residente principal e ao responsável pelo registro
        vehicle = Vehicle.objects.create(
            condominium=condo,
            registered_by=user,
            owner=apartment.main_resident,
            **validated_data
        )
        return vehicle

    def update(self, instance, validated_data):
        user, _, apartment = get_user_condo_apartment(self.context, validated_data)

        plate = validated_data.get('plate')
        color = validated_data.get('color')
        model = validated_data.get('model')

        if model:
            validated_data['model'] = model.title()

        if plate:
            validated_data['plate'] = plate.upper()

        if color:
            validated_data['color'] = color.title()

        if apartment:
            if user.apartment != apartment:
                instance.owner = apartment.main_resident


        return super().update(instance, validated_data)

class OccurrenceSerializer(serializers.ModelSerializer):

    condominium = CondominiumSerializer(read_only=True)
    number_apartment = serializers.IntegerField(write_only=True, required=False)
    block_apartment = serializers.CharField(write_only=True, required=False)
    code_condominium = serializers.CharField(write_only=True, required=False)
    reported_by = PersonSerializer(read_only=True)

    class Meta:
        model = Occurrence
        fields = (
            'id', 'title', 'description', 'status',
            'date_reported', 'condominium', 'reported_by',
            'number_apartment', 'block_apartment', 'code_condominium'
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
            reported_by=apartment.main_resident,
            title=title.title(),
            status=status.lower(),
            **validated_data
        )
        return occurrence


    def update(self, instance, validated_data):

        title = validated_data.pop('title', None)
        status = validated_data.pop('status', None)

        user, _, apartment = get_user_condo_apartment(self.context, validated_data)

        if apartment:
            if user.apartment != apartment:
                instance.reported_by = apartment.main_resident

        if title:
            validated_data['title'] = title.title()

        if status:
            validated_data['status'] = status.lower()

        return super().update(instance, validated_data)

class OrderSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    owner = PersonSerializer(read_only=True)

    number_apartment = serializers.IntegerField(write_only=True, required=False)
    block_apartment = serializers.CharField(write_only=True, required=False)
    code_condominium = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Order
        fields = (
            'id', 'order_code', 'status', 'code_condominium', 'condominium',
            'signature_image', 'registered_by', 'owner', 'number_apartment', 'block_apartment'
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
        code = validated_data.get('order_code')
        if code:
            validated_data['order_code'] = code.upper()

        # Criar o pedido associando-o ao residente principal
        order = Order.objects.create(
            condominium=condo,
            owner=apartment.main_resident,
            registered_by=user,
            **validated_data
        )
        return order

    def update(self, instance, validated_data):
        user, _, apartment = get_user_condo_apartment(self.context, validated_data)

        if apartment:
            if user.apartment != apartment:
                instance.owner = apartment.main_resident

        code = validated_data.get('order_code')
        if code:
            validated_data['order_code'] = code.upper()

        return super().update(instance, validated_data)

class NoticeSerializer(serializers.ModelSerializer):
    author = PersonSerializer(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    code_condominium = serializers.CharField(write_only=True, required=False)

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


# Communication Serializer
class CommunicationSerializer(serializers.ModelSerializer):
    sender = PersonSerializer(read_only=True)
    recipients = PersonSerializer(many=True, read_only=True)
    condominium = CondominiumSerializer(read_only=True)

    code_condominium = serializers.CharField(write_only=True, required=False)
    number_apartment = serializers.IntegerField(write_only=True, required=False)
    block_apartment = serializers.CharField(write_only=True, required=False)
    all_residents = serializers.BooleanField(write_only=True, required=False, default=False)

    class Meta:
        model = Communication
        fields = (
            'id', 'title', 'message', 'created_at', 'number_apartment', 'block_apartment',
            'sender', 'recipients', 'condominium', 'code_condominium', 'communication_type',
            'all_residents'
        )
        read_only_fields = ('id', 'created_at', 'sender', 'recipients', 'condominium')

    def validate(self, data):
        user = getuser(self.context['request'])
        if not self.instance:
            if user.user_type == 'admin':
                if not data.get('code_condominium'):
                    raise serializers.ValidationError('O código do condomínio é obrigatório para administradores.')

                if data.get('communication_type') == Communication.CommunicationTypeChoices.NOTICE:
                    if data.get('all_residents') and data.get('all_residents') is False:
                        raise serializers.ValidationError(
                            'O número do apartamento e bloco são obrigatórios se "all_residents" não for True.'
                        )

                if data.get('communication_type') == Communication.CommunicationTypeChoices.MESSAGE:
                    if not data.get('number_apartment') or not data.get('block_apartment'):
                        raise serializers.ValidationError('Número e bloco do apartamento são obrigatórios para mensagens.')

        return data

    def create(self, validated_data):

        user, condominium, apartment = get_user_condo_apartment(self.context, validated_data)

        comm_type = validated_data.get('communication_type', Communication.CommunicationTypeChoices.MESSAGE)

        if comm_type == Communication.CommunicationTypeChoices.MESSAGE:
            if user.user_type not in ['admin', 'employee']:
                recipients_qs = Person.objects.filter(
                    user_type__in=['admin', 'employee'],
                    condominium=condominium
                )
            else:
                if apartment:
                    recipients_qs = apartment.main_resident
                else:
                    raise serializers.ValidationError(
                        'Número e bloco do apartamento são obrigatórios para mensagens.'
                    )
        else:
            if user.user_type not in ['admin', 'employee']:
                raise serializers.ValidationError('Somente administração pode criar avisos.')
            if apartment:
                recipients_qs = apartment.main_resident
            else:
                recipients_qs = Person.objects.filter(
                    user_type='resident',
                    condominium=condominium
                )


        final_recipients = None

        if not recipients_qs:
            raise serializers.ValidationError(
                'Nenhum destinatário encontrado para a comunicação, talvez não tenha moradores.'
            )
        elif isinstance(recipients_qs, Person):
            final_recipients = [recipients_qs]
        else:
            final_recipients = recipients_qs

        communication = Communication.objects.create(
            sender=user,
            condominium=condominium,
            **validated_data
        )
        communication.recipients.set(final_recipients)
        return communication

    def update(self, instance, validated_data):
        if 'title' in validated_data:
            title = validated_data['title'].title()
            validated_data['title'] = title

        if (instance.communication_type  == Communication.CommunicationTypeChoices.MESSAGE
                and self.context['request'].user.user_type in ['admin', 'employee']):
            if 'number_apartment' in validated_data or 'block_apartment' in validated_data:
                user, _, apartment = get_user_condo_apartment(self.context, validated_data)

                if apartment:
                    if user.apartment != apartment:
                        instance.recipients.set([apartment.main_resident])

        if instance.communication_type == Communication.CommunicationTypeChoices.NOTICE:
            if 'number_apartment' in validated_data or 'block_apartment' in validated_data:
                user, _, apartment = get_user_condo_apartment(self.context, validated_data)

                if apartment:
                    if user.apartment != apartment:
                        instance.recipients.set([apartment.main_resident])

        return super().update(instance, validated_data)


