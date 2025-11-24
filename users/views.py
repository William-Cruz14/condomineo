from allauth.core.internal.httpkit import redirect
from decouple import config
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import Apartment, Condominium
from utils.utils import send_custom_email
from .authentication import JWTAuthenticationAllowInactive
from .filters import queryset_filter_person, PersonFilterSet
from .models import Person
from .permissions import IsOnboardingUser
from .serializers import PersonSerializer, CustomUserDetailsSerializer

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client


class CustomOAuth2Client(OAuth2Client):
    def __init__(self, *args, **kwargs):
        kwargs.pop("scope_delimiter", None)
        super().__init__(*args, **kwargs)

class PersonView(ModelViewSet):
    serializer_class = PersonSerializer
    filterset_class = PersonFilterSet
    authentication_classes = [JWTAuthenticationAllowInactive]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Person.objects.none()
        query_base = Person.objects.select_related('apartment', 'condominium')
        return queryset_filter_person(query_base, user)

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ['update', 'partial_update']:
            return [IsAuthenticated(), DjangoModelPermissions(), IsOnboardingUser()]
        return [IsAuthenticated(), DjangoModelPermissions()]

    def create(self, request, *args, **kwargs):
        if request.data.get('user_type') == Person.UserType.ADMIN:
            return Response(
                {"detail": "Criação de administradores não é permitida via esta API."},
                status=status.HTTP_403_FORBIDDEN
            )

        user = request.user
        instance = None

        # Tenta encontrar o usuário logado
        if user and user.is_authenticated:
            instance = Person.objects.filter(pk=user.pk).first()

        # Se não achou pelo login (raro), tenta pelo email enviado
        if not instance and request.data.get('email'):
            instance = Person.objects.filter(email=request.data['email']).first()

        # Decide se é Update ou Create
        if instance:
            print(f"Completando cadastro do usuário: {instance.email}")
            # Passamos 'instance', o que faz o serializer entrar no modo UPDATE
            serializer = self.get_serializer(instance, data=request.data, partial=True)
        else:
            print("Criando novo usuário")
            # Sem 'instance', o serializer entra no modo CREATE
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        # Executa o salvamento (update ou create interno do serializer)
        self.perform_create(serializer)

        # Notificação apenas se for cadastro novo ou completando agora
        if not instance or (instance and not instance.is_active):
            self.send_new_user_notification(serializer.data)

        headers = self.get_success_headers(serializer.data)

        # Retorna 200 se atualizou, 201 se criou
        return Response(serializer.data, status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        # Salva os dados. Se houver usuário logado, garante o vínculo (caso não tenha ainda)
        user = self.request.user
        if user and user.is_authenticated:
            serializer.save(user=user)
        else:
            serializer.save()


    def send_new_user_notification(self, user_data):
        condominium_id = self._get_condominium_id_from_user_data(user_data)
        if not condominium_id: return

        admins = Person.objects.filter(managed_condominiums__id=condominium_id, user_type='admin')
        if not admins.exists(): return

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
        if user_data.get('user_type') == 'resident':
            apartment_data = user_data.get('apartment')
            if apartment_data:
                apt_id = apartment_data.get('id') if isinstance(apartment_data, dict) else apartment_data
                if apt_id:
                    try:
                        return Apartment.objects.select_related('condominium').get(id=apt_id).condominium.id
                    except Apartment.DoesNotExist:
                        return None
        else:
            condominium_code = user_data.get('condominium')
            if condominium_code:
                try:
                    return Condominium.objects.get(code_condominium=condominium_code).id
                except Condominium.DoesNotExist:
                    return None
        return None

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = self.request.user
        if not user.is_authenticated:
            return Response({"detail": "Não autenticado"}, status=status.HTTP_401_UNAUTHORIZED)
        profile = Person.objects.filter(pk=user.pk)
        serializer = self.get_serializer(profile, many=True)
        return Response(serializer.data)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = config('CALLBACK_URL')


    def get_object(self):
        return self.request.user

    def post(self, request, *args, **kwargs):
        try:
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
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)