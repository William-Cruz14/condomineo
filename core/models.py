from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from rest_framework.exceptions import ValidationError

# CustomUser Manager para gerenciar a criação de usuários e superusuários
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, user_type = 'morador', **extra_fields):
        """
        Cria e salva um usuário do tipo morador por padrão com o e-mail e senha fornecidos.
        """
        if not email:
            raise ValueError('O email é obrigatório')

        email = self.normalize_email(email)
        user = self.model(email=email, user_type = user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Cria e salva um superusuário com o e-mail e senha fornecidos.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Criando um modelo personalizado que abranja Sindico, Morador e Administração
class CustomUser(AbstractUser):
    # Definindo os campos do modelo
    username = models.CharField(max_length=150, unique=True, blank=True, null=False)
    name = models.CharField(verbose_name='Nome Completo', max_length=255)
    document = models.CharField(max_length=20, unique=True, verbose_name='Documento de Identificação')
    telephone = models.CharField(max_length=11, blank=True, null=True, verbose_name='Telefone')

    # Definindo os tipos de usuários disponíveis
    USER_TYPE_CHOICES = [

        ('morador', 'Morador'),
        ('sindico', 'Sindico'),
        ('admin', 'Administrador'),
    ]

    # Definindo o campo de tipo de usuário
    user_type = models.CharField(
        verbose_name='Tipo de Usuário',
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='morador',
    )
    # Definindo o campo de apartamento
    apartment = models.ForeignKey(
        'Apartment',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='apartamentos',
    )

    objects = CustomUserManager()

    first_name = None
    last_name = None

    email = models.EmailField(verbose_name='E-mail', max_length=255, unique=True)
    entry_date = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'document', 'user_type', 'telephone'] # Campos obrigatórios

    def __str__(self):
        return f"{self.name}"

    # Validando os dados antes de salvar
    def clean(self):
        if self.user_type == 'morador' and not self.apartment:
            raise ValidationError("Um morador deve estar vinculado a um apartamento.")

    # Validando alguns dados antes de salvar
    def save(self, *args, **kwargs):

        if not self.username:
            self.username = self.email

        if self.user_type in ['sindico', 'admin']:
            self.is_staff = True
            self.is_superuser = True

        super().save(*args, **kwargs)

# Definindo o modelo de Apartamento
class Apartment(models.Model):
    # Definindo os campos do modelo
    number = models.CharField(max_length=10, unique=True)
    block = models.CharField(max_length=10)
    floor = models.IntegerField()

    def __str__(self):
        return f"Apartamento {self.number} - Bloco {self.block}"

# Definindo o modelo de Visitante
class Visitor(models.Model):
    # Definindo os campos do modelo
    name = models.CharField(max_length=255)
    document = models.CharField(max_length=20, unique=True)
    telephone = models.CharField(max_length=11, blank=True, null=True)
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='visitors')
    registered_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='registered_visitors')
    entry_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Visitante {self.name} - Apartamento {self.apartment.number}"

# Definindo o modelo de Reserva
class Reservation(models.Model):
    # Definindo os tipos de espaços disponíveis para reserva
    spaces = [
        ('salão_de_festas', 'Salão de Festas'),
        ('churrasqueira', 'Churrasqueira'),
        ('piscina', 'Piscina'),
        ('quadra', 'Quadra Poliesportiva'),
        ('playground', 'Playground'),
        ('academia', 'Academia'),
    ]
    # Definindo os campos do modelo
    resident = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reservations')
    space = models.CharField(max_length=50, choices=spaces, verbose_name='Espaço')
    date = models.DateField(verbose_name='Data')
    time = models.TimeField(verbose_name='Hora de Início')
    end_time = models.TimeField(verbose_name='Hora de Fim', blank=True, null=True)

    # Validando os dados antes de salvar
    def save(self, *args, **kwargs):
        if not self.end_time:
            raise ValueError("Hora de fim é obrigatória.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reserva - {self.space} - {self.resident.name} - {self.date} {self.time}"

# Definindo o modelo de Comunicação
class Communication(models.Model):
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='mensagens_enviadas'
    )
    to_all_moradores = models.BooleanField(default=False, verbose_name='Enviar para todos os moradores')
    recipient = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='mensagens_recebidas'
    )
    subject = models.CharField(max_length=255, verbose_name='Assunto')
    message = models.TextField(verbose_name='Mensagem')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Data e Hora')

    def __str__(self):
        if self.to_all_moradores:
            return f"De: {self.sender.name} Para: Todos os Moradores - {self.subject}"
        return f"De: {self.sender.name} Para: {self.recipient.name} - {self.subject}"

    # Validando alguns dados antes de salvar
    def clean(self):
        from django.core.exceptions import ValidationError

        if self.to_all_moradores and self.recipient:
            raise ValidationError(
                "Não é possível enviar para todos os moradores e para um destinatário específico ao mesmo tempo."
            )

        if not self.to_all_moradores and not self.recipient:
            raise ValidationError("Selecione um destinatário ou marque para enviar a todos os moradores.")

    # Validando o envio de mensagens e salvando
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Finance(models.Model):
    # Definindo os campos do modelo
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='finance')
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor")
    date = models.DateTimeField(auto_now=True,verbose_name='Data')
    description = models.TextField(verbose_name='Descrição')
    document = models.FileField(
        upload_to='financeiro_doc/',
        blank=True, null=True,
        verbose_name="Comprovante"
    )

    def __str__(self):
        return f"Financeiro - {self.creator.name} - {self.date} - {self.value}"