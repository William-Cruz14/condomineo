from decouple import config
from rest_framework import status
from rest_framework.decorators import action
from .serializers import CustomUserDetailsSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Apartment, Condominium
from utils.utils import send_custom_email
from .filters import queryset_filter_person, PersonFilterSet
from .models import Person
from .permissions import IsOnboardingUser
from .serializers import PersonSerializer
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class CustomOAuth2Client(OAuth2Client):
    def __init__(self, *args, **kwargs):
        # Evita erro de múltiplos valores para 'scope_delimiter'
        kwargs.pop("scope_delimiter", None)
        super().__init__(*args, **kwargs)

class PersonView(ModelViewSet):
    serializer_class = PersonSerializer
    filterset_class = PersonFilterSet

    def get_queryset(self):
        user = self.request.user
        query_base = Person.objects.select_related('apartment', 'condominium')
        return queryset_filter_person(query_base, user)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]

        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated() , DjangoModelPermissions() , IsOnboardingUser()]

        return [IsAuthenticated(), DjangoModelPermissions()]

    def create(self, request, *args, **kwargs):
        # Se o tipo de usuário for 'admin', retornar erro 403 (Forbidden)
        if request.data.get('user_type') == Person.UserType.ADMIN:
            return Response({"Aviso": "Criação de administradores não é permitida via esta API."},
                            status=status.HTTP_403_FORBIDDEN)

        response = super().create(request, *args, **kwargs)

        if response.status_code == 201:
            self.send_new_user_notification(response.data)

        return response


    def send_new_user_notification(self, user_data):
        """
        Busca os administradores e envia o e-mail de notificação de novo usuário.
        """
        condominium_id = self._get_condominium_id_from_user_data(user_data)

        if not condominium_id:
            print("Não foi possível determinar o condomínio para enviar a notificação.")
            return

        admins = Person.objects.filter(
            managed_condominiums__id=condominium_id,
            user_type='admin'
        )

        if not admins.exists():
            print(f"Nenhum administrador encontrado para o condomínio ID {condominium_id}.")
            return

        context = {
            'name': user_data.get('name'),
            'email': user_data.get('email'),
            'condominium' : user_data.get('condominium'),
            'apartment': user_data.get('apartment') if user_data.get('user_type') == 'resident' else 'N/A',
            'position': user_data.get('position') if user_data.get('user_type') == 'employee' else 'N/A',
            'telephone': user_data.get('telephone'),
            'user_type': "Morador" if user_data.get('user_type') == 'resident' else "Funcionário",
        }

        recipient_list = [admin.email for admin in admins]

        send_custom_email(
            subject="🎉 Novo cadastro realizado!",
            template_name='emails/new_user_email.html',
            context=context,
            recipient_list=recipient_list
        )


    def _get_condominium_id_from_user_data(self, user_data):
        """
        Lógica auxiliar para obter o ID do condomínio a partir dos dados do usuário.
        """
        if user_data.get('user_type') == 'resident':
            apartment_data = user_data.get('apartment')
            if apartment_data and apartment_data.get('id'):
                try:
                    apartment = Apartment.objects.select_related('condominium').get(id=apartment_data['id'])
                    return apartment.condominium.id
                except Apartment.DoesNotExist:
                    return None
        else:
            condominium_code = user_data.get('condominium')
            if condominium_code:
                try:
                    condominium = Condominium.objects.get(code_condominium=condominium_code)
                    return condominium.id
                except Condominium.DoesNotExist:
                    return None
        return None
    @action(detail=False, methods=['get'])
    def me(self, request):
        user = self.request.user
        profile = Person.objects.filter(id=user.id)
        serializer = self.get_serializer(profile, many=True)

        return Response(serializer.data)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = CustomOAuth2Client

    def get_object(self):
        return self.request.user


    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if self.user and not self.user.is_active:
            refresh = RefreshToken.for_user(self.user)
            refresh['restricted_signup'] = True

            user_serializer = CustomUserDetailsSerializer(self.user, context={'request': request})

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'detail': "Cadastro incompleto. Por favor, complete seu perfil.",
                'user': user_serializer.data,
            }, status=status.HTTP_200_OK)

        return response
