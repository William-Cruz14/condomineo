from rest_framework.permissions import BasePermission

class IsOnboardingUser(BasePermission):
    """
    Permite acesso apenas se o usuário tiver um token com a claim 'restrito_ao_cadastro'.
    """
    def has_permission(self, request, view):
        # A nossa lógica de validação vai aqui
        if request.auth.get('restrito_ao_cadastro'):
            return True
        return False