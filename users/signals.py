from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from users.models import Person

User = get_user_model()

@receiver(post_migrate)
def create_user_group_and_permissions(sender, **kwargs):
    """
    Cria grupos padrão e associa permissões após as migrations.
    """
    default_groups = {
        'Moradores': [
            'view_visitor', 'add_visitor', 'change_visitor', 'delete_visitor',
            'view_visit', 'add_visit', 'change_visit', 'delete_visit',
            'view_reservation', 'add_reservation', 'change_reservation', 'delete_reservation',
            'view_message', 'add_message', 'change_message', 'delete_message',
            'view_apartment',
            'view_finance',
            'view_vehicle',
            'view_order',
        ],
        'Funcionários': [
            'view_visitor', 'add_visitor', 'change_visitor', 'delete_visitor',
            'view_visit', 'add_visit', 'change_visit', 'delete_visit',
            'view_reservation', 'add_reservation', 'change_reservation', 'delete_reservation',
            'view_message', 'add_message', 'change_message', 'delete_message',
            'view_apartment', 'add_apartment', 'change_apartment',
            'view_finance', 'add_finance', 'change_finance',
            'view_vehicle', 'add_vehicle', 'change_vehicle',
            'view_order', 'add_order', 'change_order'
        ],
        'Administração': [
            'view_visitor', 'add_visitor', 'change_visitor', 'delete_visitor',
            'view_visit', 'add_visit', 'change_visit', 'delete_visit',
            'view_reservation', 'add_reservation', 'change_reservation', 'delete_reservation',
            'view_message', 'add_message', 'change_message', 'delete_message',
            'view_apartment', 'add_apartment', 'change_apartment', 'delete_apartment',
            'view_finance', 'add_finance', 'change_finance', 'delete_finance',
            'view_vehicle', 'add_vehicle', 'change_vehicle', 'delete_vehicle',
            'view_order', 'add_order', 'change_order', 'delete_order',
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

            print(f'Usuário "{instance.name}" adicionado ao grupo "{group.name}".')
        except Group.DoesNotExist:
            print(f'Grupo para o tipo de usuário "{instance.user_type}" não encontrado.')