from rest_framework import serializers
from .models import Person, Visitor, Reservation, Communication, Apartment, Finance, Vehicle, Orders, Visit
from users.models import Profile

# Serializer para Profile (autenticação)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'email', 'first_name', 'last_name')

# Serializer para Person (domínio)
class PersonSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = Person
        fields = ('id', 'name', 'document', 'telephone', 'user_type', 'profile')

class VisitorSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Visitor
        fields = ('id', 'name', 'document', 'registered_by',)


class ReservationSerializer(serializers.ModelSerializer):

    # O campo 'resident' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    resident = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Reservation
        fields = ('id', 'resident', 'space', 'start_time', 'end_time')

class CommunicationSerializer(serializers.ModelSerializer):

    # O campo 'recipients' é um campo de chave estrangeira que permite selecionar vários usuários
    recipients = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(),
        many=True,
    )
    # O campo 'sender' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Communication
        fields = ('id', 'sender', 'subject', 'message', 'sent_at', 'recipients')

class FinanceSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Finance
        fields = ('id', 'creator', 'value', 'date', 'description', 'document')

class ApartmentSerializer(serializers.ModelSerializer):
    # O campo 'residents' é um campo de chave estrangeira que permite selecionar vários usuários
    residents = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all(),
        many=True,
        required=False,
    )


    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)
    visitors = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Apartment
        fields = ('id', 'number', 'block', 'tread','residents', 'visitors', 'entry_date', 'occupation', 'registered_by')

class VisitSerializer(serializers.ModelSerializer):
    # O campo 'visitor' é um campo de chave estrangeira que permite selecionar um visitante
    visitor = PersonSerializer()
    # O campo 'apartment' é um campo de chave estrangeira que permite selecionar um apartamento
    apartment = ApartmentSerializer()
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Visit
        fields = ('id', 'visitor', 'apartment', 'entry_date', 'observation','exit_date', 'registered_by')


class VehicleSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Vehicle
        fields = ('id', 'registered_by', 'plate', 'model', 'color', 'owner')


class OrdersSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Orders
        fields = ('id', 'order_code', 'status', 'signature_image', 'registered_by',)
        read_only_fields = ('signature_image',)