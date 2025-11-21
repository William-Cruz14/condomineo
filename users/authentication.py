
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken


class JWTAuthenticationAllowInactive(JWTAuthentication):
    """
    Autenticação JWT que PERMITE usuários inativos (is_active=False).
    Usado apenas no endpoint de completar cadastro.
    """

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken("Token não contém identificador do usuário")

        try:
            user = self.user_model.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed("Usuário não encontrado", code="user_not_found")

        # AQUI ESTAVA O BLOQUEIO:
        # O original tem: if not user.is_active: raise AuthenticationFailed(...)
        # Nós simplesmente removemos essa checagem e retornamos o usuário.

        return user