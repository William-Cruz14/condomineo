from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from users.models import Person
from .models import (
    Address, Condominium, Apartment, Visitor, Visit,
    Occurrence, Reservation, Finance, Vehicle, Order,
    Notice, Communication, Resident
)


class AddressModelTests(TestCase):
    """Testes para o modelo Address"""

    def setUp(self):
        self.address_data = {
            'street': 'Rua das Flores',
            'number': 123,
            'complement': 'Bloco 1',
            'neighborhood': 'Centro',
            'city': 'São Paulo',
            'state': 'SP',
            'zip_code': '12345000'
        }

    def test_create_address_successfully(self):
        """Testa criação bem-sucedida de endereço"""
        address = Address.objects.create(**self.address_data)
        self.assertIsNotNone(address.id)
        self.assertEqual(address.street, 'Rua das Flores')
        self.assertEqual(address.number, 123)

    def test_address_str_representation(self):
        """Testa representação string do endereço"""
        address = Address.objects.create(**self.address_data)
        expected = 'Rua das Flores, 123 - São Paulo/SP'
        self.assertEqual(str(address), expected)

    def test_address_without_complement(self):
        """Testa criação de endereço sem complemento"""
        data = self.address_data.copy()
        data.pop('complement')
        address = Address.objects.create(**data)
        self.assertIsNone(address.complement)


class CondominiumModelTests(TestCase):
    """Testes para o modelo Condominium"""

    @classmethod
    def setUpTestData(cls):
        cls.creator = Person.objects.create_user(
            password='strong-pass',
            user_type='admin',
            name='Admin Condo',
            cpf='11122233344',
            email='admin@example.com'
        )
        cls.address = Address.objects.create(
            street='Rua das Flores',
            number=123,
            complement='Bloco 1',
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='12345000'
        )

    def test_code_condominium_auto_generated_uppercase(self):
        """Testa geração automática do código do condomínio em maiúsculas"""
        condo = Condominium.objects.create(
            name='Residencial Primavera',
            cnpj='12345678901234',
            address=self.address,
            created_by=self.creator
        )

        self.assertEqual(len(condo.code_condominium), 8)
        self.assertTrue(condo.code_condominium.isupper())

    def test_str_returns_human_readable_value(self):
        """Testa representação string do condomínio"""
        condo = Condominium.objects.create(
            name='Residencial Outono',
            cnpj='22345678901234',
            address=self.address,
            created_by=self.creator
        )

        expected = f'{condo.name} ({condo.code_condominium})'
        self.assertEqual(str(condo), expected)

    def test_cnpj_unique_constraint(self):
        """Testa constraint de unicidade do CNPJ"""
        Condominium.objects.create(
            name='Residencial A',
            cnpj='11111111111111',
            address=self.address,
            created_by=self.creator
        )

        address2 = Address.objects.create(
            street='Rua B',
            number=456,
            neighborhood='Bairro',
            city='Cidade',
            state='ST',
            zip_code='11111000'
        )

        with self.assertRaises(Exception):
            Condominium.objects.create(
                name='Residencial B',
                cnpj='11111111111111',
                address=address2,
                created_by=self.creator
            )

    def test_condominium_has_created_at(self):
        """Testa se condomínio tem data de criação"""
        condo = Condominium.objects.create(
            name='Residencial C',
            cnpj='33333333333333',
            address=self.address,
            created_by=self.creator
        )
        self.assertIsNotNone(condo.created_at)


class ApartmentModelTests(TestCase):
    """Testes para o modelo Apartment"""

    def setUp(self):
        self.creator = Person.objects.create_user(
            password='strong-pass',
            user_type='admin',
            name='Admin User',
            cpf='12345678901',
            email='admin@test.com'
        )

        self.address = Address.objects.create(
            street='Rua Test',
            number=100,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='12345000'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Test',
            cnpj='12345678000199',
            address=self.address,
            created_by=self.creator
        )

    def test_create_apartment_successfully(self):
        """Testa criação bem-sucedida de apartamento"""
        apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=101,
            block='A',
            tread=1,
            occupation=Apartment.Occupation.UNOCCUPIED
        )
        self.assertIsNotNone(apartment.id)
        self.assertEqual(apartment.number, 101)

    def test_apartment_str_representation(self):
        """Testa representação string do apartamento"""
        apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=201,
            block='B',
            tread=2
        )
        expected = f'Apartamento 201 - Bloco B - Piso 2 ({self.condominium.name})'
        self.assertEqual(str(apartment), expected)

    def test_unique_apartment_per_condo(self):
        """Testa constraint de unicidade de apartamento por condomínio"""
        Apartment.objects.create(
            condominium=self.condominium,
            number=301,
            block='C',
            tread=3
        )

        with self.assertRaises(ValidationError):
            apt = Apartment(
                condominium=self.condominium,
                number=301,
                block='C',
                tread=3
            )
            apt.save()

    def test_exit_date_validation(self):
        """Testa validação de data de saída"""
        # Cria apartamento primeiro para ter entry_date
        apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=401,
            block='D',
            tread=4
        )

        # Tenta definir exit_date antes de entry_date
        apartment.exit_date = apartment.entry_date - timedelta(days=1)

        with self.assertRaises(ValidationError):
            apartment.clean()

    def test_default_occupation_is_unoccupied(self):
        """Testa que ocupação padrão é 'desocupado'"""
        apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=501,
            block='E',
            tread=5
        )
        self.assertEqual(apartment.occupation, Apartment.Occupation.UNOCCUPIED)


class VisitorModelTests(TestCase):
    """Testes para o modelo Visitor"""

    def setUp(self):
        self.creator = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin',
            cpf='11111111111',
            email='admin@visitor.com'
        )

        address = Address.objects.create(
            street='Rua A',
            number=1,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='11111111'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Visitor',
            cnpj='11111111000111',
            address=address,
            created_by=self.creator
        )

    def test_create_visitor_successfully(self):
        """Testa criação bem-sucedida de visitante"""
        visitor = Visitor.objects.create(
            condominium=self.condominium,
            name='João Silva',
            cpf='12345678900',
            telephone='11999999999',
            registered_by=self.creator
        )
        self.assertIsNotNone(visitor.id)
        self.assertEqual(visitor.name, 'João Silva')

    def test_visitor_str_representation(self):
        """Testa representação string do visitante"""
        visitor = Visitor.objects.create(
            condominium=self.condominium,
            name='Maria Santos',
            cpf='98765432100',
            registered_by=self.creator
        )
        self.assertEqual(str(visitor), 'Visitante Maria Santos')

    def test_visitor_unique_cpf_per_condominium(self):
        """Testa unicidade de CPF por condomínio"""
        Visitor.objects.create(
            condominium=self.condominium,
            name='Pedro',
            cpf='11111111111',
            registered_by=self.creator
        )

        with self.assertRaises(Exception):
            Visitor.objects.create(
                condominium=self.condominium,
                name='Paulo',
                cpf='11111111111',
                registered_by=self.creator
            )


class VisitModelTests(TestCase):
    """Testes para o modelo Visit"""

    def setUp(self):
        self.creator = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin',
            cpf='11111111111',
            email='admin@visit.com'
        )

        address = Address.objects.create(
            street='Rua B',
            number=2,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='22222222'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Visit',
            cnpj='22222222000111',
            address=address,
            created_by=self.creator
        )

        self.apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=101,
            block='A',
            tread=1
        )

        self.visitor = Visitor.objects.create(
            condominium=self.condominium,
            name='Visitante Teste',
            cpf='33333333333',
            registered_by=self.creator
        )

    def test_create_visit_successfully(self):
        """Testa criação bem-sucedida de visita"""
        visit = Visit.objects.create(
            condominium=self.condominium,
            visitor=self.visitor,
            apartment=self.apartment,
            observation='Visita social',
            registered_by=self.creator
        )
        self.assertIsNotNone(visit.id)
        self.assertIsNotNone(visit.entry_date)

    def test_visit_exit_date_validation(self):
        """Testa validação de data de saída"""
        visit = Visit(
            condominium=self.condominium,
            visitor=self.visitor,
            apartment=self.apartment,
            registered_by=self.creator,
            exit_date=timezone.now() - timedelta(hours=1)
        )

        with self.assertRaises(ValidationError):
            visit.clean()


class OccurrenceModelTests(TestCase):
    """Testes para o modelo Occurrence"""

    def setUp(self):
        self.creator = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin',
            cpf='44444444444',
            email='admin@occurrence.com'
        )

        address = Address.objects.create(
            street='Rua C',
            number=3,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='33333333'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Occurrence',
            cnpj='33333333000111',
            address=address,
            created_by=self.creator
        )

    def test_create_occurrence_successfully(self):
        """Testa criação bem-sucedida de ocorrência"""
        occurrence = Occurrence.objects.create(
            condominium=self.condominium,
            title='Barulho Excessivo',
            description='Barulho no apartamento 201',
            status=Occurrence.StatusChoices.OPEN,
            reported_by=self.creator
        )
        self.assertIsNotNone(occurrence.id)
        self.assertEqual(occurrence.status, Occurrence.StatusChoices.OPEN)

    def test_occurrence_str_representation(self):
        """Testa representação string da ocorrência"""
        occurrence = Occurrence.objects.create(
            condominium=self.condominium,
            title='Teste Ocorrência',
            description='Descrição',
            reported_by=self.creator
        )
        expected = f'Ocorrência: Teste Ocorrência - Reportado por: {self.creator.name}'
        self.assertEqual(str(occurrence), expected)

    def test_occurrence_default_status_is_open(self):
        """Testa que status padrão é 'aberta'"""
        occurrence = Occurrence.objects.create(
            condominium=self.condominium,
            title='Nova Ocorrência',
            description='Teste',
            reported_by=self.creator
        )
        self.assertEqual(occurrence.status, Occurrence.StatusChoices.OPEN)


class ReservationModelTests(TestCase):
    """Testes para o modelo Reservation"""

    def setUp(self):
        self.admin = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin',
            cpf='55555555555',
            email='admin@reservation.com'
        )

        address = Address.objects.create(
            street='Rua D',
            number=4,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='44444444'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Reservation',
            cnpj='44444444000111',
            address=address,
            created_by=self.admin
        )

        self.apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=102,
            block='A',
            tread=1
        )

        self.resident = Person.objects.create_user(
            password='pass123',
            user_type='resident',
            name='Morador Teste',
            cpf='66666666666',
            email='resident@test.com',
            condominium=self.condominium,
            apartment=self.apartment
        )

    def test_create_reservation_successfully(self):
        """Testa criação bem-sucedida de reserva"""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=4)

        reservation = Reservation.objects.create(
            condominium=self.condominium,
            resident=self.resident,
            space=Reservation.SpaceChoices.PARTY_ROOM,
            start_time=start_time,
            end_time=end_time
        )
        self.assertIsNotNone(reservation.id)

    def test_reservation_time_validation(self):
        """Testa validação de horário de reserva"""
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time - timedelta(hours=1)

        reservation = Reservation(
            condominium=self.condominium,
            resident=self.resident,
            space=Reservation.SpaceChoices.BARBECUE,
            start_time=start_time,
            end_time=end_time
        )

        with self.assertRaises(ValidationError):
            reservation.clean()

    def test_reservation_conflict_validation(self):
        """Testa validação de conflito de reservas"""
        start_time = timezone.now() + timedelta(days=2)
        end_time = start_time + timedelta(hours=4)

        Reservation.objects.create(
            condominium=self.condominium,
            resident=self.resident,
            space=Reservation.SpaceChoices.POOL,
            start_time=start_time,
            end_time=end_time
        )

        conflicting_start = start_time + timedelta(hours=2)
        conflicting_end = conflicting_start + timedelta(hours=4)

        reservation2 = Reservation(
            condominium=self.condominium,
            resident=self.resident,
            space=Reservation.SpaceChoices.POOL,
            start_time=conflicting_start,
            end_time=conflicting_end
        )

        with self.assertRaises(ValidationError):
            reservation2.save()


class FinanceModelTests(TestCase):
    """Testes para o modelo Finance"""

    def setUp(self):
        self.creator = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin Finance',
            cpf='77777777777',
            email='admin@finance.com'
        )

        address = Address.objects.create(
            street='Rua E',
            number=5,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='55555555'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Finance',
            cnpj='55555555000111',
            address=address,
            created_by=self.creator
        )

    def test_create_finance_successfully(self):
        """Testa criação bem-sucedida de registro financeiro"""
        finance = Finance.objects.create(
            condominium=self.condominium,
            creator=self.creator,
            value=Decimal('1500.50'),
            description='Pagamento de manutenção'
        )
        self.assertIsNotNone(finance.id)
        self.assertEqual(finance.value, Decimal('1500.50'))

    def test_finance_value_validation(self):
        """Testa validação de valor maior que zero"""
        finance = Finance(
            condominium=self.condominium,
            creator=self.creator,
            value=Decimal('-100.00'),
            description='Teste'
        )

        with self.assertRaises(ValidationError):
            finance.clean()

    def test_finance_description_required(self):
        """Testa que descrição é obrigatória"""
        finance = Finance(
            condominium=self.condominium,
            creator=self.creator,
            value=Decimal('100.00'),
            description=''
        )

        with self.assertRaises(ValidationError):
            finance.clean()


class VehicleModelTests(TestCase):
    """Testes para o modelo Vehicle"""

    def setUp(self):
        self.admin = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin Vehicle',
            cpf='88888888888',
            email='admin@vehicle.com'
        )

        address = Address.objects.create(
            street='Rua F',
            number=6,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='66666666'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Vehicle',
            cnpj='66666666000111',
            address=address,
            created_by=self.admin
        )

        self.apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=103,
            block='A',
            tread=1
        )

        self.owner = Person.objects.create_user(
            password='pass123',
            user_type='resident',
            name='Proprietário Veículo',
            cpf='99999999999',
            email='owner@test.com',
            condominium=self.condominium,
            apartment=self.apartment
        )

    def test_create_vehicle_successfully(self):
        """Testa criação bem-sucedida de veículo"""
        vehicle = Vehicle.objects.create(
            condominium=self.condominium,
            registered_by=self.admin,
            plate='ABC1234',
            model='Civic',
            color='Preto',
            owner=self.owner
        )
        self.assertIsNotNone(vehicle.id)
        self.assertEqual(vehicle.plate, 'ABC1234')

    def test_vehicle_str_representation(self):
        """Testa representação string do veículo"""
        vehicle = Vehicle.objects.create(
            condominium=self.condominium,
            registered_by=self.admin,
            plate='XYZ5678',
            model='Corolla',
            color='Branco',
            owner=self.owner
        )
        expected = f'Veículo Corolla - XYZ5678 - Proprietário: {self.owner.name}'
        self.assertEqual(str(vehicle), expected)

    def test_vehicle_unique_plate_per_condominium(self):
        """Testa unicidade de placa por condomínio"""
        Vehicle.objects.create(
            condominium=self.condominium,
            registered_by=self.admin,
            plate='AAA1111',
            model='Gol',
            color='Azul',
            owner=self.owner
        )

        with self.assertRaises(Exception):
            Vehicle.objects.create(
                condominium=self.condominium,
                registered_by=self.admin,
                plate='AAA1111',
                model='Palio',
                color='Vermelho',
                owner=self.owner
            )


class OrderModelTests(TestCase):
    """Testes para o modelo Order"""

    def setUp(self):
        self.admin = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin Order',
            cpf='10101010101',
            email='admin@order.com'
        )

        address = Address.objects.create(
            street='Rua G',
            number=7,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='77777777'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Order',
            cnpj='77777777000111',
            address=address,
            created_by=self.admin
        )

        self.apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=104,
            block='A',
            tread=1
        )

        self.owner = Person.objects.create_user(
            password='pass123',
            user_type='resident',
            name='Destinatário',
            cpf='20202020202',
            email='recipient@test.com',
            condominium=self.condominium,
            apartment=self.apartment
        )

    def test_create_order_successfully(self):
        """Testa criação bem-sucedida de encomenda"""
        order = Order.objects.create(
            condominium=self.condominium,
            registered_by=self.admin,
            order_code='PKG12345',
            owner=self.owner
        )
        self.assertIsNotNone(order.id)
        self.assertEqual(order.status, Order.StatusChoices.RECEIVED)

    def test_order_code_required_validation(self):
        """Testa validação de código obrigatório"""
        order = Order(
            condominium=self.condominium,
            registered_by=self.admin,
            order_code='',
            owner=self.owner
        )

        with self.assertRaises(ValidationError):
            order.clean()

    def test_order_str_representation(self):
        """Testa representação string da encomenda"""
        order = Order.objects.create(
            condominium=self.condominium,
            registered_by=self.admin,
            order_code='PKG99999',
            owner=self.owner
        )
        expected = f'Encomenda PKG99999 - {order.status} - {self.owner}'
        self.assertEqual(str(order), expected)


class NoticeModelTests(TestCase):
    """Testes para o modelo Notice"""

    def setUp(self):
        self.author = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin Notice',
            cpf='30303030303',
            email='admin@notice.com'
        )

        address = Address.objects.create(
            street='Rua H',
            number=8,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='88888888'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Notice',
            cnpj='88888888000111',
            address=address,
            created_by=self.author
        )

    def test_create_notice_successfully(self):
        """Testa criação bem-sucedida de aviso"""
        notice = Notice.objects.create(
            condominium=self.condominium,
            title='Manutenção Programada',
            content='Haverá manutenção no elevador na próxima semana',
            author=self.author
        )
        self.assertIsNotNone(notice.id)
        self.assertEqual(notice.title, 'Manutenção Programada')

    def test_notice_str_representation(self):
        """Testa representação string do aviso"""
        notice = Notice.objects.create(
            condominium=self.condominium,
            title='Aviso Importante',
            content='Conteúdo do aviso',
            author=self.author
        )
        expected = f'Aviso: Aviso Importante - Autor: {self.author.name}'
        self.assertEqual(str(notice), expected)

    def test_notice_has_timestamps(self):
        """Testa que aviso tem timestamps de criação e atualização"""
        notice = Notice.objects.create(
            condominium=self.condominium,
            title='Teste',
            content='Teste',
            author=self.author
        )
        self.assertIsNotNone(notice.created_at)
        self.assertIsNotNone(notice.updated_at)


class CommunicationModelTests(TestCase):
    """Testes para o modelo Communication"""

    def setUp(self):
        self.sender = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin Communication',
            cpf='40404040404',
            email='admin@communication.com'
        )

        address = Address.objects.create(
            street='Rua I',
            number=9,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='99999999'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Communication',
            cnpj='99999999000111',
            address=address,
            created_by=self.sender
        )

        self.apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=105,
            block='A',
            tread=1
        )

        self.recipient = Person.objects.create_user(
            password='pass123',
            user_type='resident',
            name='Morador Destinatário',
            cpf='50505050505',
            email='recipient@communication.com',
            condominium=self.condominium,
            apartment=self.apartment
        )

    def test_create_communication_successfully(self):
        """Testa criação bem-sucedida de comunicação"""
        communication = Communication.objects.create(
            condominium=self.condominium,
            communication_type=Communication.CommunicationTypeChoices.MESSAGE,
            title='Mensagem Importante',
            message='Conteúdo da mensagem',
            sender=self.sender
        )
        communication.recipients.add(self.recipient)

        self.assertIsNotNone(communication.id)
        self.assertEqual(communication.recipients.count(), 1)

    def test_communication_str_representation(self):
        """Testa representação string da comunicação"""
        communication = Communication.objects.create(
            condominium=self.condominium,
            communication_type=Communication.CommunicationTypeChoices.NOTICE,
            title='Comunicado',
            message='Teste',
            sender=self.sender
        )
        expected = f'Comunicação: Comunicado - Remetente: {self.sender.name}'
        self.assertEqual(str(communication), expected)

    def test_communication_all_residents_flag(self):
        """Testa flag de envio para todos os moradores"""
        communication = Communication.objects.create(
            condominium=self.condominium,
            communication_type=Communication.CommunicationTypeChoices.MESSAGE,
            title='Para Todos',
            message='Mensagem geral',
            sender=self.sender,
            all_residents=True
        )
        self.assertTrue(communication.all_residents)


class ResidentModelTests(TestCase):
    """Testes para o modelo Resident (Dependente)"""

    def setUp(self):
        self.admin = Person.objects.create_user(
            password='pass123',
            user_type='admin',
            name='Admin Resident',
            cpf='60606060606',
            email='admin@resident.com'
        )

        address = Address.objects.create(
            street='Rua J',
            number=10,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='10101010'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Resident',
            cnpj='10101010000111',
            address=address,
            created_by=self.admin
        )

        self.apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=106,
            block='A',
            tread=1
        )

        self.main_resident = Person.objects.create_user(
            password='pass123',
            user_type='resident',
            name='Morador Principal',
            cpf='70707070707',
            email='mainresident@test.com',
            condominium=self.condominium,
            apartment=self.apartment
        )

    def test_create_resident_successfully(self):
        """Testa criação bem-sucedida de dependente"""
        dependent = Resident.objects.create(
            condominium=self.condominium,
            name='João Dependente',
            cpf='80808080808',
            email='dependent@test.com',
            phone='11988888888',
            registered_by=self.main_resident,
            apartment=self.apartment
        )
        self.assertIsNotNone(dependent.id)
        self.assertEqual(dependent.name, 'João Dependente')

    def test_resident_cpf_unique(self):
        """Testa unicidade de CPF do dependente"""
        Resident.objects.create(
            condominium=self.condominium,
            name='Maria Dependente',
            cpf='90909090909',
            registered_by=self.main_resident,
            apartment=self.apartment
        )

        with self.assertRaises(Exception):
            Resident.objects.create(
                condominium=self.condominium,
                name='Pedro Dependente',
                cpf='90909090909',
                registered_by=self.main_resident,
                apartment=self.apartment
            )

    def test_resident_has_created_at(self):
        """Testa que dependente tem data de criação"""
        dependent = Resident.objects.create(
            condominium=self.condominium,
            name='Ana Dependente',
            cpf='10203040506',
            registered_by=self.main_resident,
            apartment=self.apartment
        )
        self.assertIsNotNone(dependent.created_at)

