from rest_framework import serializers
from .models import Visitor, Reservation, Apartment, Finance, Vehicle, Order, Visit, Condominium

class CondominiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condominium
        fields = (
            'id', 'name', 'road', 'number', 'complement', 'cnpj',
            'code_condominium', 'created_at', 'created_by'
        )

        extra_kwargs = {
            'code_condominium': {'read_only': True},
            'created_at': {'read_only': True},
            'created_by': {'read_only': True},
        }


class VisitorSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    condominium_id = serializers.PrimaryKeyRelatedField(
        queryset=Condominium.objects.all(),
        source='condominium',
        write_only=True
    )

    class Meta:
        model = Visitor
        fields = ('id', 'name', 'cpf', 'telephone', 'registered_by', 'condominium', 'condominium_id')



class ReservationSerializer(serializers.ModelSerializer):

    # O campo 'resident' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    resident = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Reservation
        fields = ('id', 'resident', 'space', 'start_time', 'end_time')



class FinanceSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    condominium_id = serializers.PrimaryKeyRelatedField(
        queryset=Condominium.objects.all(),
        source='condominium',
        write_only=True
    )

    class Meta:
        model = Finance
        fields = ('id', 'creator', 'value', 'date', 'description', 'document', 'condominium', 'condominium_id')

class ApartmentSerializer(serializers.ModelSerializer):
    condominium = serializers.PrimaryKeyRelatedField(queryset=Condominium.objects.all())
    condominium_detail = CondominiumSerializer(source='condominium', read_only=True)

    class Meta:
        model = Apartment
        fields = (
            'id', 'number', 'block', 'tread', 'entry_date', 'exit_date',
            'occupation', 'condominium', 'condominium_detail'
        )

class VisitSerializer(serializers.ModelSerializer):
    # O campo 'visitor' é um campo de chave estrangeira que permite selecionar um visitante
    visitor = VisitorSerializer(read_only=True)
    # O campo 'apartment' é um campo de chave estrangeira que permite selecionar um apartamento
    apartment = ApartmentSerializer(read_only=True)
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Visit
        fields = ('id', 'visitor', 'apartment', 'entry_date', 'observation','exit_date', 'registered_by')


class VehicleSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)
    condominium = CondominiumSerializer(read_only=True)
    condominium_id = serializers.PrimaryKeyRelatedField(
        queryset=Condominium.objects.all(),
        source='condominium',
        write_only=True
    )

    class Meta:
        model = Vehicle
        fields = ('id', 'registered_by', 'plate', 'model', 'color', 'garage', 'owner', 'condominium', 'condominium_id')


class OrderSerializer(serializers.ModelSerializer):
    # O campo 'registered_by' é somente leitura, pois é preenchido automaticamente com o usuário autenticado
    registered_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'order_code', 'status', 'signature_image', 'registered_by', 'owner')
        read_only_fields = ('signature_image',)