from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permite que o usuário que tem qualquer relacionamento com o objeto (owner, creator, registered_by, sender, recipient)
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        # checar se o usuário tem qualquer relacionamento com o objeto
        for field in ('owner', 'creator', 'registered_by', 'sender', 'recipients', 'created_by'):
            if hasattr(obj, field):
                if getattr(obj, field) == user:
                    return True
        
        # verifica se o usuário gerencia o condomínio
        condo = getattr(obj, 'condominium', None)
        if condo and getattr(user, 'user_type', None) == 'admin' and user.managed_condominiums.filter(id=condo.id).exists():
            return True
        return False


class IsResident(permissions.BasePermission):
    """
    Permite acesso apenas a moradores.
    """
    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and getattr(user, 'user_type', None) == 'resident'
