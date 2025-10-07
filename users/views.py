from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from django.core.mail import send_mail
from decouple import config
from core.models import Apartment
from .models import Person
from .serializers import PersonSerializer

class PersonView(ModelViewSet):
    serializer_class = PersonSerializer

    def get_queryset(self):
        user = self.request.user

        # Administrador vê pessoas dos condomínios que gerencia
        if user.user_type == 'admin':
            managed_condos = user.managed_condominiums.all()
            return Person.objects.filter(
                apartment__condominium__in=managed_condos
            ).union(
                Person.objects.filter(managed_condominiums__in=managed_condos)
            )

        # Morador vê apenas pessoas do mesmo condomínio
        if user.apartment:
            return Person.objects.filter(id=user.id)

        # Funcionário vê apenas pessoas do condomínio onde trabalha
        return Person.objects.filter(registered_by=user)
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]

        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        # Se o tipo de usuário for 'admin', retornar erro 403 (Forbidden)
        if request.data.get('user_type') == 'admin':
            return Response({"Aviso": "Criação de administradores não é permitida para todos.."},
                            status=status.HTTP_403_FORBIDDEN)

        # Se o tipo de usuário for 'resident' e um apartamento for fornecido, marca o apartamento como 'ocupado'
        if request.data.get('user_type') == 'resident' and request.data.get('apartment'):
            apartment_id = request.data.get('apartment')
            try:
                apartment = Apartment.objects.get(id=apartment_id)
                apartment.occupation = 'occupied'
                apartment.save()
            except Apartment.DoesNotExist:
                return Response({"error": "Apartamento não encontrado."},
                                status=status.HTTP_400_BAD_REQUEST)


        response = super().create(request, *args, **kwargs)

        if response.status_code == 201:
            new_user_data = response.data
            apartment_id = new_user_data.get('apartment')
            print(f"Apartamento ID: {apartment_id}")
            condominium_id = None


            if apartment_id:
                try:
                    apartment = Apartment.objects.get(id=apartment_id)
                    condominium_id = apartment.condominium.id
                    print(f"Condominio ID: {condominium_id}")
                except Apartment.DoesNotExist:
                    pass

            if condominium_id:
                print("Estou enviando email")
                print(condominium_id)
                admins = Person.objects.filter(
                    managed_condominiums__id=condominium_id,
                    user_type='admin'
                )

                subject = "Cadastro Realizado"
                message = f"Olá, o usuário {new_user_data.get('name')} acaba de ser cadastrado.."
                from_email = config('EMAIL_HOST_USER')
                recipient_list = [admin.email for admin in admins]

                send_mail(subject, message, from_email, recipient_list)

        return response

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = self.request.user
        profile = Person.objects.filter(id=user.id)
        serializer = self.get_serializer(profile, many=True)

        return Response(serializer.data)

