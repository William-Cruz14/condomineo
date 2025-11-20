from rest_framework.permissions import BasePermission

class IsOnboardingUser(BasePermission):
    """
    Permite acesso apenas se o usuário tiver um token com a claim 'restrito_ao_cadastro'.
    """
    def has_permission(self, request, view):
        # A nossa lógica de validação vai aqui
        if request.auth and request.auth.get('restricted_signup'):
            return True
        return False