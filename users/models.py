from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from rest_framework import validators
from django.core.exceptions import ValidationError

# CustomUserManager para gerenciar a criação de usuários e superusuários
class CustomPersonManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        extra_fields.pop('is_active', None)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        if extra_fields.get('user_type') == 'admin' or extra_fields.get('is_superuser'):
            user.is_active = True
        else:
            user.is_active = False

        user.full_clean()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superusuário deve ter is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superusuário deve ter is_superuser=True.')
        return self.create_user(email, name, password, **extra_fields)


# Criando um modelo personalizado que abranja Sindico, Morador e Ad ministração
class Person(AbstractUser):

    class UserType(models.TextChoices):
        RESIDENT = 'resident', 'Morador'
        EMPLOYEE = 'employee', 'Funcionário'
        ADMIN = 'admin', 'Administrador'

    username = None
    name = models.CharField(verbose_name='Nome Completo', max_length=255)
    email = models.EmailField(verbose_name='E-mail', max_length=255, unique=True)
    cpf = models.CharField(
        max_length=11, unique=True,
        null=True, blank=True, verbose_name='Cadastro de Pessoa Física (CPF)'
    )

    telephone = models.CharField(max_length=11, blank=True, null=True, verbose_name='Telefone')
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.RESIDENT,
        verbose_name='Tipo de Usuário'
    )

    position = models.CharField(max_length=50, blank=True, null=True, verbose_name='Cargo')

    condominium = models.ForeignKey(
        'core.Condominium',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Codomínio',
        help_text='Condomínio associado ao funcionário ou morador.'
    )

    apartment = models.OneToOneField(
        'core.Apartment',
        related_name='main_resident',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        unique=True,
        verbose_name='Apartamento',
        help_text= 'Selecione o apartamento associado ao morador.'
    )

    managed_condominiums = models.ManyToManyField(
        'core.Condominium',
        related_name='managers',
        blank=True,
        verbose_name='Condomínios Gerenciados',
        help_text='Selecione os condomínios que este usuário pode gerenciar.'
    )
    registered_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Registrado por',
        related_name='registered_users',
        help_text='Usuário que registrou este usuário.'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'user_type', 'cpf']

    objects = CustomPersonManager()

    class Meta:
        verbose_name = 'Pessoa'
        verbose_name_plural = 'Pessoas'
        ordering = ['name']


    def clean(self):
        super().clean()
        if self.user_type == "resident" and not self.apartment:
            raise ValidationError('Moradores devem ter um apartamento associado.')

        if self.user_type in ["resident", "employee"] and not self.condominium:
            raise ValidationError("Usuários que não são administradores devem ter um condomínio associado.")

        if self.user_type == "employee" and not self.position:
            raise ValidationError("Funcionários devem ter um cargo definido.")

        if self.apartment:
            if self.apartment.main_resident != self:
                raise ValidationError("Apartamento já possui um morador principal associado.")

        if self.user_type == Person.UserType.ADMIN and self.is_superuser == False:
            if self.pk and self.managed_condominiums.count() == 0:
                raise ValidationError("Administradores devem gerenciar pelo menos um condomínio.")


    def approve_person(self):
        """Aprova o usuário, ativando sua conta."""
        if not self.is_active:
            self.is_active = True
            self.save()

    def __str__(self):
        return f'{self.name}'