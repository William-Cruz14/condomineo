import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from users.models import Person

class Condominium(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nome do Condomínio')
    cnpj = models.CharField(max_length=20, unique=True, verbose_name='Cadastro Nacional da Pessoa Jurídica (CNPJ)')
    address = models.OneToOneField(
        'core.Address',
        on_delete=models.CASCADE,
        related_name='condominium',
        verbose_name='Endereço'
    )
    code_condominium = models.CharField(max_length=20, unique=True, verbose_name='Código do Condomínio')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    created_by = models.ForeignKey(
       'users.Person',
        on_delete=models.CASCADE,
        related_name='created_condominiums',
        verbose_name='Criado por'
    )

    class Meta:
        verbose_name = 'Condomínio'
        verbose_name_plural = 'Condomínios'

    def save(self, *args, **kwargs):
        # Garantir que o código do condomínio seja sempre armazenado em maiúsculas
        if not self.code_condominium:
            self.code_condominium = str(uuid.uuid4().hex[:8]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code_condominium})"

class Address(models.Model):
    street = models.CharField(max_length=255, verbose_name='Rua')
    number = models.CharField(max_length=20, verbose_name='Número')
    complement = models.CharField(max_length=100, blank=True, null=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=100, verbose_name='Bairro')
    city = models.CharField(max_length=100, verbose_name='Cidade')
    state = models.CharField(max_length=100, verbose_name='Estado')
    zip_code = models.CharField(max_length=20, verbose_name='CEP')

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):
        return f'{self.street}, {self.number} - {self.city}/{self.state}'

# Definindo o modelo de Visitante
class Visitor(models.Model):
    # Definindo os campos do modelo
    condominium = models.ForeignKey(
        'core.Condominium',
        on_delete=models.CASCADE,
        related_name='visitors',
        verbose_name='Condomínio'
    )
    name = models.CharField(max_length=255, verbose_name='Nome do Visitante')
    cpf = models.CharField(
        max_length=11,
        verbose_name='Cadastro de Pessoa Física (CPF)',
        help_text='Apenas números, sem pontos ou traços.'
    )
    telephone = models.CharField(max_length=11, blank=True, null=True, verbose_name='Telefone do Visitante')
    registered_by = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='registered_visitors',
        verbose_name='Cadastrado por',
    )

    class Meta:
        verbose_name = 'Visitante'
        verbose_name_plural = 'Visitantes'
        unique_together = ('cpf', 'condominium')

    def __str__(self):
        return f'Visitante {self.name}'


# Definindo o modelo de Apartamento
class Apartment(models.Model):
    # Definindo os campos do modelo
    condominium = models.ForeignKey(
        'core.Condominium',
        on_delete=models.CASCADE,
        related_name='apartments',
        verbose_name='Condomínio'
    )
    number = models.IntegerField(verbose_name='Número do Apartamento')
    block = models.CharField(max_length=10, verbose_name='Bloco')
    tread = models.IntegerField(verbose_name='Piso', blank=True, null=True)

    class Occupation(models.TextChoices):
        OCCUPIED = 'occupied', 'Ocupado'
        UNOCCUPIED = 'unoccupied', 'Desocupado'

    entry_date = models.DateField(auto_now_add=True, verbose_name='Data de Entrada')
    exit_date = models.DateField(null=True, blank=True, verbose_name='Data de Saída')
    occupation = models.CharField(
        max_length=20,
        choices=Occupation.choices,
        default=Occupation.UNOCCUPIED,
        verbose_name='Ocupação',
        help_text='Selecione o status de ocupação do apartamento.'
    )

    class Meta:
        verbose_name = 'Apartamento'
        verbose_name_plural = 'Apartamentos'
        constraints = [
            models.UniqueConstraint(fields=['number', 'block', 'condominium'], name='unique_apartment_per_condo')
        ]

    def __str__(self):
        return f'Apartamento {self.number} - Bloco {self.block} - Piso {self.tread} ({self.condominium.name})'

    def clean(self, *args, **kwargs):
        # usa ValidationError do Django
        super().clean()

        if self.exit_date and self.entry_date and self.exit_date <= self.entry_date:
            raise ValidationError('A data de saída deve ser posterior à data de entrada.')

        if not self.number or not self.block or not self.condominium:
            raise ValidationError('O número, bloco e condomínio são obrigatórios.')

        if Apartment.objects.filter(
                number=self.number, block=self.block,
                tread=self.tread, condominium=self.condominium).exclude(pk=self.pk).exists():
            raise ValidationError('Já existe um apartamento com este número, bloco e piso.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

# Definindo o modelo de Visita
class Visit(models.Model):
    # Definindo os campos do modelo
    visitor = models.ForeignKey(
        'core.Visitor',
        on_delete=models.CASCADE,
        # changed related_name to plural for clarity
        related_name='visits',
        verbose_name='Visitante',
    )

    apartment = models.ForeignKey(
        'core.Apartment',
        on_delete=models.CASCADE,
        # changed related_name to plural for clarity
        related_name='visits',
        verbose_name='Apartamento',
    )

    observation = models.TextField(blank=True, null=True, verbose_name='Observação')
    entry_date = models.DateTimeField(auto_now_add=True, verbose_name='Data da Visita')
    exit_date = models.DateTimeField(blank=True, null=True, verbose_name='Data de Saída')
    registered_by = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='registered_visits',
        verbose_name='Cadastrado por',
    )

    class Meta:
        verbose_name = 'Visita'
        verbose_name_plural = 'Visitas'
        ordering = ['entry_date']

    def __str__(self):
        return (f'Visita de {self.visitor.name} ao Apartamento {self.apartment.number} '
                f'- Entrada: {self.entry_date} - Saída: {self.exit_date}')

    def clean(self):
        if self.exit_date and self.exit_date <= self.entry_date:
            raise ValidationError('A data de saída deve ser posterior à data de entrada.')

# Definindo o modelo de Reserva
class Reservation(models.Model):
    # Definindo os tipos de espaços disponíveis para reserva
    class SpaceChoices(models.TextChoices):
        PARTY_ROOM = 'salão_de_festas', 'Salão de Festas'
        BARBECUE = 'churrasqueira', 'Churrasqueira'
        POOL = 'piscina', 'Piscina'
        COURT = 'quadra', 'Quadra Poliesportiva'
        PLAYGROUND = 'playground', 'Playground'
        GYM = 'academia', 'Academia'

    # Definindo os campos do modelo
    resident = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Morador',
    )

    space = models.CharField(
        max_length=20,
        choices=SpaceChoices.choices,
        default=SpaceChoices.PARTY_ROOM,
        verbose_name='Espaço',
        help_text='Selecione o espaço que deseja reservar.'
    )
    start_time = models.DateTimeField(verbose_name='Data e Hora Início')
    end_time = models.DateTimeField(verbose_name='Data e Hora de Fim', blank=True, null=True)

    # Validando os dados antes de salvar
    def clean(self, *args, **kwargs):
        super().clean()

        if not self.end_time:
            raise ValidationError('Hora de fim é obrigatória.')

        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValidationError('A hora de fim deve ser posterior à hora de início.')

        # evita conflitos entre condomínios diferentes; filtra pela propriedade condominium do residente
        condominium = None
        if getattr(self, 'resident', None):
            condominium = self.resident.condominium
            print(f'Condomínio do residente: {condominium.name}')

        conflicting_reservations = Reservation.objects.filter(
            space=self.space,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        ).exclude(pk=self.pk)

        if condominium:
            conflicting_reservations = conflicting_reservations.filter(resident__condominium=condominium)

        if conflicting_reservations.exists():
            raise ValidationError('Já existe uma reserva para este espaço nesse horário.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f'Reserva - {self.space} - {self.resident.name} - {self.start_time} {self.end_time}'


class Finance(models.Model):
    # Definindo os campos do modelo
    condominium = models.ForeignKey(
        'core.Condominium',
        on_delete=models.CASCADE,
        related_name='finances',
        verbose_name='Condomínio'
    )
    creator = models.ForeignKey(
        'users.Person',
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

    def clean(self):
        if self.value <= 0:
            raise ValidationError('O valor deve ser maior que zero.')

        if not self.description:
            raise ValidationError('A descrição é obrigatória.')


class Vehicle(models.Model):
    # Definindo os campos do modelo
    condominium = models.ForeignKey(
        'core.Condominium',
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name='Condomínio'
    )
    registered_by = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='registered_vehicles',
        verbose_name='Cadastrado por'
    )
    plate = models.CharField(max_length=10, verbose_name='Placa do Veículo')
    model = models.CharField(max_length=50, verbose_name='Modelo do Veículo')
    color = models.CharField(max_length=20, verbose_name='Cor do Veículo')
    owner = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='vehicles',
        verbose_name='Proprietário'
    )
    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        constraints = [
            models.UniqueConstraint(fields=['plate', 'condominium'], name='unique_plate_per_condo')
        ]

    def __str__(self):
        return f'Veículo {self.model} - {self.plate} - Proprietário: {self.owner.name}'


class Order(models.Model):
    # Definindo os tipos de 'status' disponíveis para o pedido
    class StatusChoices(models.TextChoices):
        RECEIVED = 'recebido', 'Recebido'
        COMPLETED = 'entregue', 'Entregue'

    registered_by = models.ForeignKey(
        'users.Person',
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
    order_code = models.CharField(max_length=20, verbose_name='Número do Pedido')
    order_date = models.DateTimeField(auto_now_add=True, verbose_name='Data do Recebimento')
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.RECEIVED,
        verbose_name='Status do Pedido',
        help_text='Selecione o status atual do pedido.'
    )
    owner = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Proprietário do Pedido'
    )

    class Meta:
        verbose_name = 'Encomenda'
        verbose_name_plural = 'Encomendas'
        ordering = ['-order_date']

    def __str__(self):
        return f'Encomenda {self.order_code} - {self.status} - {self.owner}'

    def clean(self):
        if not self.order_code:
            raise ValidationError('O código do pedido é obrigatório.')


class Notice(models.Model):
    # Definindo os campos do modelo
    condominium = models.ForeignKey(
        'core.Condominium',
        on_delete=models.CASCADE,
        related_name='notices',
        verbose_name='Condomínio'
    )
    title = models.CharField(max_length=255, verbose_name='Título')
    content = models.TextField(verbose_name='Conteúdo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')
    file_complement = models.FileField(
        upload_to='notice_files/',
        blank=True,
        null=True,
        verbose_name='Arquivo Complementar',
        help_text='Anexe um arquivo relacionado ao aviso, se necessário.'
    )
    author = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='notices',
        verbose_name='Autor'
    )

    class Meta:
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'

    def __str__(self):
        return f'Aviso: {self.title} - Autor: {self.author.name}'


class Communication(models.Model):
    # Definindo os campos do modelo
    condominium = models.ForeignKey(
        'core.Condominium',
        on_delete=models.CASCADE,
        related_name='communications',
        verbose_name='Condomínio'
    )
    title = models.CharField(max_length=255, verbose_name='Título')
    message = models.TextField(verbose_name='Mensagem')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Criação')
    sender = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='sent_communications',
        verbose_name='Remetente'
    )
    recipients = models.ManyToManyField(
        Person,
        related_name='received_communications',
        verbose_name='Destinatários'
    )

    class Meta:
        verbose_name = 'Comunicação'
        verbose_name_plural = 'Comunicações'

    def __str__(self):
        return f'Comunicação: {self.title} - Remetente: {self.sender.name}'


class Resident(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nome do Morador')
    cpf = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='Cadastro de Pessoa Física (CPF)',
        help_text='Apenas números, sem pontos ou traços.'
    )
    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name='Telefone do Morador'
    )
    registered_by = models.ForeignKey(
        'users.Person',
        on_delete=models.CASCADE,
        related_name='registered_residents',
        verbose_name='Morador Principal'
    )
    apartment = models.ForeignKey(
        'core.Apartment',
        on_delete=models.CASCADE,
        related_name='dependents',
        verbose_name='Apartamento'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )

    class Meta:
        verbose_name = 'Dependente'
        verbose_name_plural = 'Dependentes'