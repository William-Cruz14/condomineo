from allauth.core.internal.httpkit import redirect
from decouple import config
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

# Imports do projeto (ajuste se necessário conforme sua estrutura de pastas)
from core.models import Apartment, Condominium
from utils.utils import send_custom_email
from .authentication import JWTAuthenticationAllowInactive
from .filters import queryset_filter_person, PersonFilterSet
from .models import Person
from .permissions import IsOnboardingUser
from .serializers import PersonSerializer, CustomUserDetailsSerializer

# Imports do dj-rest-auth e allauth
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

    # AQUI ESTÁ O SEGREDO: Usamos a auth que aceita inativos
    authentication_classes = [JWTAuthenticationAllowInactive]

    def get_queryset(self):
        user = self.request.user
        # Se por acaso chegar um anônimo no GET, retorna vazio
        if not user.is_authenticated:
            return Person.objects.none()

        query_base = Person.objects.select_related('apartment', 'condominium')
        return queryset_filter_person(query_base, user)

    def get_permissions(self):
        # CREATE deve ser AllowAny para permitir que o request chegue
        # até a authentication_classes e seja processado, mesmo se o token for de inativo.
        if self.action == 'create':
            return [AllowAny()]

        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), DjangoModelPermissions(), IsOnboardingUser()]

        return [IsAuthenticated(), DjangoModelPermissions()]

    def create(self, request, *args, **kwargs):
        # Se o tipo de usuário for 'admin', retornar erro 403 (Forbidden)
        if request.data.get('user_type') == Person.UserType.ADMIN:
            return Response(
                {"detail": "Criação de administradores não é permitida via esta API."},
                status=status.HTTP_403_FORBIDDEN
            )

        response = super().create(request, *args, **kwargs)

        if response.status_code == 201:
            self.send_new_user_notification(response.data)

        return response

    def perform_create(self, serializer):
        """
        Intercepta a criação para vincular ao usuário do Google, se existir.
        MANTÉM O USUÁRIO INATIVO conforme regra de negócio (síndico aprova).
        """
        user = self.request.user

        # Se veio autenticado (Google, mesmo inativo)
        if user and user.is_authenticated:
            print(f"Vinculando cadastro ao usuário Google: {user.email}")
            # Vincula a Person ao User
            serializer.save(user=user)
            # NÃO ativamos o usuário aqui. Ele continua is_active=False.
        else:
            # Cadastro normal (sem Google/Token)
            serializer.save()

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
            'condominium': user_data.get('condominium'),
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
            # Suporta tanto dicionário (ID dentro) quanto ID direto
            if apartment_data:
                apt_id = apartment_data.get('id') if isinstance(apartment_data, dict) else apartment_data
                if apt_id:
                    try:
                        apartment = Apartment.objects.select_related('condominium').get(id=apt_id)
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
        if not user.is_authenticated:
            return Response({"detail": "Não autenticado"}, status=status.HTTP_401_UNAUTHORIZED)

        profile = Person.objects.filter(user=user)  # Ajustado para filtrar por user field
        serializer = self.get_serializer(profile, many=True)

        return Response(serializer.data)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = CustomOAuth2Client
    callback_url = config('CALLBACK_URL')  # ou valor fixo se preferir

    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)

            # Se o usuário existe mas está inativo (comportamento padrão),
            # geramos um token especial para ele conseguir completar o cadastro.
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
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)