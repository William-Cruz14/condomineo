from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from users.models import Person
from core.models import Visitor, Visit, Reservation, Apartment, Finance, Vehicle, Order, Notice

User = get_user_model()

@receiver(post_migrate)
def create_user_group_and_permissions(sender, **kwargs):
    """
    Cria grupos padrão e associa permissões após as migrations.
    """
    # Apenas processar quando o app relacionado termina suas migrações
    app_label = getattr(sender, 'label', '')
    if app_label not in ['users', 'core', 'auth']:
        return

    # Criar os grupos se não existirem
    morador_group, _ = Group.objects.get_or_create(name='Moradores')
    funcionario_group, _ = Group.objects.get_or_create(name='Funcionários')
    admin_group, _ = Group.objects.get_or_create(name='Administração')

    # Limpar permissões existentes para evitar duplicações
    morador_group.permissions.clear()
    funcionario_group.permissions.clear()
    admin_group.permissions.clear()

    # Obter os modelos que precisamos
    models_map = {
        'visitor': Visitor,
        'visit': Visit,
        'reservation': Reservation,
        'apartment': Apartment,
        'finance': Finance,
        'vehicle': Vehicle,
        'order': Order,
        'notice': Notice,
    }

    # Definir as permissões por grupo
    moradores_perms = {
        'visitor': ['view', 'add', 'change', 'delete'],
        'visit': ['view', 'add', 'change', 'delete'],
        'reservation': ['view', 'add', 'change', 'delete'],
        'apartment': ['view', 'add'],
        'finance': ['view'],
        'vehicle': ['view'],
        'order': ['view'],
        'notice': ['view'],
    }

    funcionarios_perms = {
        'visitor': ['view', 'add', 'change', 'delete'],
        'visit': ['view', 'add', 'change', 'delete'],
        'reservation': ['view', 'add', 'change', 'delete'],
        'apartment': ['view', 'add', 'change'],
        'finance': ['view', 'add', 'change'],
        'vehicle': ['view', 'add', 'change'],
        'order': ['view', 'add', 'change'],
        'notice': ['view', 'add', 'change'],
    }

    administracao_perms = {
        'visitor': ['view', 'add', 'change', 'delete'],
        'visit': ['view', 'add', 'change', 'delete'],
        'reservation': ['view', 'add', 'change', 'delete'],
        'apartment': ['view', 'add', 'change', 'delete'],
        'finance': ['view', 'add', 'change', 'delete'],
        'vehicle': ['view', 'add', 'change', 'delete'],
        'order': ['view', 'add', 'change', 'delete'],
        'notice': ['view', 'add', 'change', 'delete'],
    }

    # Função para adicionar permissões a um grupo
    def add_permissions_to_group(group, perms_dict):
        for model_name, actions in perms_dict.items():
            if model_name not in models_map:
                continue

            model = models_map[model_name]
            content_type = ContentType.objects.get_for_model(model)

            # Construir uma única consulta para obter todas as permissões de uma vez
            q_objects = Q()
            for action in actions:
                q_objects |= Q(codename=f"{action}_{model_name}")

            # Obter permissões com uma única consulta
            permissions = Permission.objects.filter(content_type=content_type).filter(q_objects)
            group.permissions.add(*permissions)

    # Aplicar permissões a cada grupo
    add_permissions_to_group(morador_group, moradores_perms)
    add_permissions_to_group(funcionario_group, funcionarios_perms)
    add_permissions_to_group(admin_group, administracao_perms)

    print("Grupos e permissões criados com sucesso.")


@receiver(post_save, sender=Person)
def assign_user_to_group(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user_type == 'resident':
                group = Group.objects.get(name='Moradores')
            elif instance.user_type == 'admin':
                group = Group.objects.get(name='Administração')
            elif instance.user_type == 'employee':
                group = Group.objects.get(name='Funcionários')

            instance.groups.add(group)
        except Group.DoesNotExist:
            print(f'Grupo para o tipo de usuário "{instance.user_type}" não encontrado.')