from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet
from django.core.mail import send_mail
from django.template.loader import render_to_string
from decouple import config
from core.models import Apartment, Condominium
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

        response = super().create(request, *args, **kwargs)
        condominium_id = None

        if response.status_code == 201:
            new_user_data = response.data
            if new_user_data.get('user_type') == 'resident':
                apartment = new_user_data.get('apartment')
                print(apartment)
                apartment_id = apartment.get('id') if apartment else None
                print(f"Apartamento ID: {apartment_id}.")

                if apartment_id:
                    try:
                        apartment = Apartment.objects.get(id=apartment_id)
                        condominium_id = apartment.condominium.id
                        print(f"Condominio ID: {condominium_id}")
                    except Apartment.DoesNotExist:
                        print("Apartamento não encontrado.")

            else:
                condominium_code = new_user_data.get('condominium')
                print(condominium_code)
                condominium_id = Condominium.objects.get(code_condominium=condominium_code).id if condominium_code else None
                print(f"Condominio ID (funcionário): {condominium_id}")

            if condominium_id:
                print("Estou enviando email")
                print(condominium_id)
                admins = Person.objects.filter(
                    managed_condominiums__id=condominium_id,
                    user_type='admin'
                )

                context = {
                    'name': new_user_data.get('name'),
                    'email': new_user_data.get('email'),
                    'telephone': new_user_data.get('telephone'),
                    'user_type': "Morador" if new_user_data.get('user_type') == 'resident' else "Funcionário",
                }

                html_message = render_to_string('emails/new_user_email.html', context)
                message = f"Olá, o usuário {context['name']} acaba de ser cadastrado no sistema."
                print(f"Admins encontrados: {admins.count()}")

                subject = "🎉 Novo cadastro realizado!"
                from_email = config('EMAIL_HOST_USER')
                recipient_list = [admin.email for admin in admins]

                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    html_message=html_message,
                )

        return response

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = self.request.user
        profile = Person.objects.filter(id=user.id)
        serializer = self.get_serializer(profile, many=True)

        return Response(serializer.data)

