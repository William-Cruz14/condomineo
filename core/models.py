from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from rest_framework.exceptions import ValidationError

# CustomUserManager para gerenciar a criação de usuários e superusuários
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


    objects = CustomUserManager()

    first_name = None
    last_name = None

    email = models.EmailField(verbose_name='E-mail', max_length=255, unique=True)
    entry_date = models.DateField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'document', 'user_type', 'telephone'] # Campos obrigatórios

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f'{self.name}'

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
    registered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='registered_apartments',
        verbose_name='Cadastrado por'
    )
    number = models.CharField(max_length=10, unique=True, verbose_name='Número do Apartamento')
    block = models.CharField(max_length=10, verbose_name='Bloco')
    tread = models.IntegerField(verbose_name='Piso')
    residents = models.ManyToManyField(
        CustomUser,
        related_name='apartments',
        verbose_name='Moradores',
        blank=True,
        help_text='Selecione os moradores que residem neste apartamento.'
    )
    entry_date = models.DateField(auto_now_add=True)
    exit_date = models.DateField(null=True, blank=True, verbose_name='Data de Saída')
    occupation = models.BooleanField(default=False, verbose_name='Ocupação')

    class Meta:
        verbose_name = 'Apartamento'
        verbose_name_plural = 'Apartamentos'

    def __str__(self):
        return f'Apartamento {self.number} - Bloco {self.block} - Piso {self.tread} - Ocupação: {self.occupation}'

# Definindo o modelo de Visitante
class Visitor(models.Model):
    # Definindo os campos do modelo
    name = models.CharField(max_length=255, verbose_name='Nome do Visitante')
    document = models.CharField(max_length=20, unique=True, verbose_name='Documento do Visitante')
    telephone = models.CharField(max_length=11, blank=True, null=True, verbose_name='Telefone do Visitante')
    observation = models.TextField(blank=True, null=True, verbose_name='Observação')
    registered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='registered_visitors',
        verbose_name='Cadastrado por'
    )
    visiting = models.ManyToManyField(
        CustomUser,
        related_name='visitors',
        verbose_name='Anfitriões',
    )
    entry_date = models.DateField(auto_now_add=True, verbose_name='Data da Visita')
    exit_date = models.DateField(blank=True, null=True, verbose_name='Data de Saída')

    class Meta:
        verbose_name = 'Visitante'
        verbose_name_plural = 'Visitantes'

    def __str__(self):
        return f'Visitante {self.name} - Cadastrado por {self.registered_by}'

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
    resident = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Morador',
    )
    space = models.CharField(max_length=50, choices=spaces, verbose_name='Espaço')
    date = models.DateField(auto_now_add=True, verbose_name='Data')
    time = models.TimeField(verbose_name='Hora de Início')
    end_time = models.TimeField(verbose_name='Hora de Fim', blank=True, null=True)

    # Validando os dados antes de salvar
    def save(self, *args, **kwargs):
        if not self.end_time:
            raise ValueError('Hora de fim é obrigatória.')
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f'Reserva - {self.space} - {self.resident.name} - {self.date} {self.time}'


# Definindo o modelo de Comunicação
class Communication(models.Model):
    # Definindo os campos do modelo
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='communications',
        verbose_name='Remetente'
    )
    subject = models.CharField(max_length=255, verbose_name='Assunto')
    message = models.TextField(verbose_name='Mensagem')
    recipients = models.ManyToManyField(
        CustomUser,
        related_name='received_communications',
        verbose_name='Destinatários',
    )

    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Data e Hora')

    class Meta:
        verbose_name = 'Comunicação'
        verbose_name_plural = 'Comunicações'

    def __str__(self):
        return f'Assunto: {self.subject} - {self.sent_at}'

    # Validando o envio de mensagens e salvando
    def save(self, *args, **kwargs):
        if not self.subject:
            raise ValidationError('O assunto é obrigatório.')
        if not self.message:
            raise ValidationError('A mensagem é obrigatória.')
        super().save(*args, **kwargs)

class Finance(models.Model):
    # Definindo os campos do modelo
    creator = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='finance',
        verbose_name='Criador'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Valor',
        help_text='Informe o valor da despesa ou receita.'
    )
    date = models.DateTimeField(auto_now=True,verbose_name='Data')
    description = models.TextField(verbose_name='Descrição')
    document = models.FileField(
        upload_to='financeiro_doc/',
        blank=True, null=True,
        verbose_name='Comprovante',
        help_text='Envie o comprovante de pagamento ou recibo.'
    )

    class Meta:
        verbose_name = 'Finança'
        verbose_name_plural = 'Finanças'

    def __str__(self):
        return f'Financeiro - {self.creator.name} - {self.date} - {self.value}'


class Vehicle(models.Model):
    # Definindo os campos do modelo
    registered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='registered_vehicles',
        verbose_name='Cadastrado por'
    )
    plate = models.CharField(max_length=10, unique=True, verbose_name='Placa do Veículo')
    model = models.CharField(max_length=50, verbose_name='Modelo do Veículo')
    color = models.CharField(max_length=20, verbose_name='Cor do Veículo')
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name='Proprietário'
    )
    garage = models.CharField(max_length=10, unique=True, verbose_name='Garagem')

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'

    def __str__(self):
        return f'Veículo {self.model} - {self.plate} - Proprietário: {self.owner.name}'


class Orders(models.Model):
    # Definindo os tipos de 'status' disponíveis para o pedido
    STATUS_CHOICES = [
        ('recebido', 'Recebido'),
        ('entregue', 'Entregue'),
    ]
    registered_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='registered_orders',
        verbose_name='Cadastrado por'
    )

    signature_image = models.FileField(
        upload_to='signature_doc/',
        blank=True,
        null=True,
        verbose_name='Comprovante',
        help_text='Anexe uma foto da assinatura.'
    )
    order_code = models.CharField(max_length=20, unique=True, verbose_name='Número do Pedido')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Data do Recebimento')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES ,verbose_name='Status do Pedido', default='recebido')
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Morador'
    )

    class Meta:
        verbose_name = 'Encomenda'
        verbose_name_plural = 'Encomendas'

    def __str__(self):
        return f'Encomenda {self.order_code} - {self.status} - {self.owner}'