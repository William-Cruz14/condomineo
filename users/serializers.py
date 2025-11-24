from dj_rest_auth.registration.serializers import SocialLoginSerializer
from rest_framework import serializers
from core.utils import get_user_condo_apartment, get_apartment_number, get_condominium_to_code, \
    pop_apartment_and_condominium
from rest_framework.exceptions import ValidationError
from utils.validators import (
    validator_cpf, validator_telephone, validator_user_type,
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
            # CRUCIAL: Desativa a validação automática de unique do email
            # para permitir que a gente trate isso na View (Upsert)
            'email': {'validators': []}
        }
        read_only_fields = (
            'id',
            'is_active',
            'registered_by',
        )

    def get_apartment(self, obj):
        if obj.apartment:
            from core.serializers import ApartmentSerializer
            return ApartmentSerializer(obj.apartment).data
        return None

    def validate_telephone(self, telephone):
        return validator_telephone(telephone)

    def validate_email(self, email):
        # Permite o e-mail se for do próprio usuário logado
        user = self.context['request'].user
        if user.is_authenticated and user.email == email:
            return email

        # Se for de outro usuário, bloqueia
        if Person.objects.exclude(id=self.instance.id if self.instance else None).filter(email=email).exists():
            raise ValidationError('Este e-mail já está em uso.')
        return email

    def validate_cpf(self, cpf):
        return validator_cpf(cpf)

    def validate_user_type(self, user_type):
        return validator_user_type(user_type)

    def validate(self, data):
        # 1. Validação de Recaptcha (Agora roda sempre, seja create ou update)
        token = data.get('recaptcha_token')  # Use get para não quebrar se não vier
        if token:
            from users.services import verificar_recaptcha
            # Remove do data para não tentar salvar no model
            data.pop('recaptcha_token')
            success, message = verificar_recaptcha(token)
            if not success:
                raise ValidationError({'recaptcha_token': message})

        # Lógica de validação comum
        user_type = data.get('user_type')

        # Se estamos atualizando (Google) ou criando do zero, precisamos validar campos obrigatórios
        # Adaptação para garantir que campos obrigatórios sejam checados mesmo no Update

        if user_type == Person.UserType.RESIDENT:
            # Para UPDATE, pegamos do data ou da instance. Para CREATE, só do data.
            number_apartment = data.get('number_apartment')
            block_apartment = data.get('block_apartment')
            code_condominium = data.get('code_condominium')

            if not number_apartment or not block_apartment or not code_condominium:
                # Se for update e os campos não vierem, pode ser que já existam?
                # No caso do cadastro inicial Google, eles NÃO existem, então vai cair aqui corretamente.
                raise ValidationError({
                    'number_apartment / block_apartment / code_condominium':
                        'Número do apartamento, bloco e código do condomínio são obrigatórios para moradores.'
                })

            if code_condominium and number_apartment and block_apartment:
                apartment = get_apartment_number(
                    get_condominium_to_code(code_condominium),
                    number_apartment,
                    block_apartment
                )
                # Verifica se apartamento existe e se já tem morador (exceto se for eu mesmo)
                if apartment:
                    if hasattr(apartment, 'main_resident') and apartment.main_resident:
                        # Se for update, verifica se o morador principal não sou eu mesmo
                        if self.instance and apartment.main_resident.id == self.instance.id:
                            pass
                        else:
                            raise ValidationError("Apartamento já possui um morador principal associado.")
                else:
                    raise ValidationError("Apartamento não encontrado para os dados fornecidos.")

        elif user_type == Person.UserType.EMPLOYEE:
            if not data.get('position') or not data.get('code_condominium'):
                raise ValidationError("Cargo e código do condomínio são obrigatórios para funcionários.")

        # Validação de CPF único (exceto o próprio)
        cpf = data.get('cpf')
        if cpf:
            exists_query = Person.objects.filter(cpf=cpf)
            if self.instance:
                exists_query = exists_query.exclude(id=self.instance.id)

            if exists_query.exists():
                raise ValidationError({'cpf': 'Este CPF já está em uso.'})

        return super().validate(data)  # Removemos validações duplicadas do super se houverem conflito

    def create(self, validated_data):
        _, condo, apartment = get_user_condo_apartment(self.context, validated_data)
        validated_data['name'] = validated_data['name'].title()

        if apartment:
            if apartment.occupation != 'occupied':
                apartment.occupation = 'occupied'
                apartment.save()
            person = Person.objects.create_user(apartment=apartment, condominium=condo, **validated_data)
        else:
            person = Person.objects.create_user(condominium=condo, **validated_data)
        return person

    def update(self, instance, validated_data):
        # O update precisa lidar com a lógica de condomínio/apartamento também
        # pois o usuário Google está "completando" esses dados agora.

        # Tenta extrair dados de condomínio se vierem
        try:
            _, condo, apartment = get_user_condo_apartment(self.context, validated_data)

            if condo:
                instance.condominium = condo

            if apartment:
                instance.apartment = apartment
                if apartment.occupation != 'occupied':
                    apartment.occupation = 'occupied'
                    apartment.save()
        except:
            # Se der erro na busca (ex: dados não enviados), segue o fluxo normal
            # ou usa a lógica existente do seu pop_apartment_and_condominium
            pass

        # Sua lógica original de update
        # Removemos do validated_data para não dar erro no super().update se não forem campos do model direto
        validated_data.pop('number_apartment', None)
        validated_data.pop('block_apartment', None)
        validated_data.pop('code_condominium', None)

        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        if 'name' in validated_data:
            validated_data['name'] = validated_data['name'].title()

        return super().update(instance, validated_data)


class CustomUserDetailsSerializer(serializers.ModelSerializer):
    is_new_user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Person
        fields = ('id', 'email', 'name', 'is_new_user')
        read_only_fields = ('id', 'email', 'name', 'is_new_user')

    def get_is_new_user(self, obj):
        if not obj.cpf:
            return True
        return False


class CustomSocialLoginSerializer(SocialLoginSerializer):
    callback_url = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        # Garante que o callback_url passe para o validated_data
        request = self.context.get('request')
        if request and 'callback_url' in request.data:
            attrs['callback_url'] = request.data['callback_url']

        return super().validate(attrs)