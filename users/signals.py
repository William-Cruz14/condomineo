from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from users.models import Profile
from core.models import Person

@receiver(post_migrate)
def create_user_group_and_permissions(sender, **kwargs):
    """
    Cria grupos padrão e associa permissões após as migrations.
    """
    default_groups = {
        'Moradores': [
            'view_visitor', 'add_visitor', 'change_visitor', 'delete_visitor',
            'view_reservation', 'add_reservation', 'change_reservation', 'delete_reservation',
            'view_communication', 'add_communication', 'change_communication', 'delete_communication',
            'view_apartment',
            'view_finance',
            'view_vehicle',
            'view_orders',
        ],
        'Síndico': [
            'view_visitor', 'add_visitor', 'change_visitor', 'delete_visitor',
            'view_reservation', 'add_reservation', 'change_reservation', 'delete_reservation',
            'view_communication', 'add_communication', 'change_communication', 'delete_communication',
            'view_apartment', 'add_apartment', 'change_apartment',
            'view_finance', 'add_finance', 'change_finance',
            'view_vehicle', 'add_vehicle', 'change_vehicle',
            'view_orders', 'add_orders', 'change_orders'
        ],
        'Administracao': [
            'view_visitor', 'add_visitor', 'change_visitor', 'delete_visitor',
            'view_reservation', 'add_reservation', 'change_reservation', 'delete_reservation',
            'view_communication', 'add_communication', 'change_communication', 'delete_communication',
            'view_apartment', 'add_apartment', 'change_apartment', 'delete_apartment',
            'view_finance', 'add_finance', 'change_finance', 'delete_finance',
            'view_vehicle', 'add_vehicle', 'change_vehicle', 'delete_vehicle',
            'view_orders', 'add_orders', 'change_orders', 'delete_orders',
        ],
    }

    for group_name, permissions in default_groups.items():
        group, _ = Group.objects.get_or_create(name=group_name)

        for codename in permissions:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                print(f'Permissão "{codename}" não encontrada.')

@receiver(post_save, sender=Person)
def assign_user_to_group(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user_type == 'morador':
                group = Group.objects.get(name='Moradores')
            elif instance.user_type == 'admin':
                group = Group.objects.get(name='Administracao')
            elif instance.user_type == 'sindico':
                group = Group.objects.get(name='Síndico')
            instance.profile.groups.add(group)
        except Group.DoesNotExist:
            print(f'Grupo para o tipo de usuário "{instance.user_type}" não encontrado.')