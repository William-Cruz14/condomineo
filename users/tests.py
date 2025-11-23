from django.core.exceptions import ValidationError
from django.test import TestCase

from core.models import Address, Condominium, Apartment
from .models import Person


class CustomPersonManagerTests(TestCase):
    """Testes para CustomPersonManager"""

    def setUp(self):
        self.address = Address.objects.create(
            street='Rua Manager',
            number=1,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='11111111'
        )

    def test_create_user_without_email_raises_error(self):
        """Testa que criar usuário sem email gera erro"""
        with self.assertRaises(ValueError) as context:
            Person.objects.create_user(
                email='',
                name='Test User',
                password='pass123'
            )
        self.assertIn('email é obrigatório', str(context.exception))

    def test_create_user_normalizes_email(self):
        """Testa que email é normalizado"""
        user = Person.objects.create_user(
            email='TEST@EXAMPLE.COM',
            name='Test User',
            cpf='11111111111',
            password='pass123',
            user_type='admin'
        )
        self.assertEqual(user.email, 'TEST@example.com')

    def test_create_user_default_inactive(self):
        """Testa que usuário padrão é criado inativo"""
        condominium = Condominium.objects.create(
            name='Condo Test',
            cnpj='12345678000199',
            address=self.address,
            created_by=Person.objects.create_user(
                email='admin@test.com',
                name='Admin',
                cpf='99999999999',
                password='pass',
                user_type='admin'
            )
        )

        apartment = Apartment.objects.create(
            condominium=condominium,
            number=101,
            block='A',
            tread=1
        )

        user = Person.objects.create_user(
            email='resident@test.com',
            name='Resident',
            cpf='22222222222',
            password='pass123',
            user_type='resident',
            condominium=condominium,
            apartment=apartment
        )
        self.assertFalse(user.is_active)

    def test_create_admin_is_active(self):
        """Testa que admin é criado ativo"""
        user = Person.objects.create_user(
            email='admin@test.com',
            name='Admin User',
            cpf='33333333333',
            password='pass123',
            user_type='admin'
        )
        self.assertTrue(user.is_active)

    def test_create_superuser_successfully(self):
        """Testa criação de superusuário"""
        superuser = Person.objects.create_superuser(
            email='super@test.com',
            name='Super User',
            cpf='44444444444',
            password='pass123',
            user_type='admin'
        )
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_active)

    def test_create_superuser_without_is_staff_raises_error(self):
        """Testa que criar superusuário sem is_staff gera erro"""
        with self.assertRaises(ValueError):
            Person.objects.create_superuser(
                email='super@test.com',
                name='Super User',
                cpf='55555555555',
                password='pass123',
                user_type='admin',
                is_staff=False
            )


class PersonModelTests(TestCase):
    """Testes para o modelo Person"""

    def setUp(self):
        self.address = Address.objects.create(
            street='Rua Person',
            number=2,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='22222222'
        )

        self.admin = Person.objects.create_user(
            email='admin@person.com',
            name='Admin Person',
            cpf='66666666666',
            password='pass123',
            user_type='admin'
        )

        self.condominium = Condominium.objects.create(
            name='Condo Person',
            cnpj='11111111000111',
            address=self.address,
            created_by=self.admin
        )

    def test_create_person_successfully(self):
        """Testa criação bem-sucedida de pessoa"""
        person = Person.objects.create_user(
            email='person@test.com',
            name='Test Person',
            cpf='77777777777',
            password='pass123',
            user_type='admin'
        )
        self.assertIsNotNone(person.id)
        self.assertEqual(person.name, 'Test Person')

    def test_person_str_representation(self):
        """Testa representação string da pessoa"""
        person = Person.objects.create_user(
            email='test@str.com',
            name='João Silva',
            cpf='88888888888',
            password='pass123',
            user_type='admin'
        )
        self.assertEqual(str(person), 'João Silva')

    def test_email_is_unique(self):
        """Testa unicidade do email"""
        Person.objects.create_user(
            email='unique@test.com',
            name='User One',
            cpf='10101010101',
            password='pass123',
            user_type='admin'
        )

        with self.assertRaises(Exception):
            Person.objects.create_user(
                email='unique@test.com',
                name='User Two',
                cpf='20202020202',
                password='pass123',
                user_type='admin'
            )

    def test_cpf_is_unique(self):
        """Testa unicidade do CPF"""
        Person.objects.create_user(
            email='user1@test.com',
            name='User One',
            cpf='12312312312',
            password='pass123',
            user_type='admin'
        )

        with self.assertRaises(Exception):
            Person.objects.create_user(
                email='user2@test.com',
                name='User Two',
                cpf='12312312312',
                password='pass123',
                user_type='admin'
            )

    def test_resident_without_apartment_raises_error(self):
        """Testa que morador sem apartamento gera erro"""
        resident = Person(
            email='resident@noapt.com',
            name='Resident No Apt',
            cpf='30303030303',
            user_type='resident',
            condominium=self.condominium
        )
        resident.set_password('pass123')

        with self.assertRaises(ValidationError) as context:
            resident.full_clean()
        self.assertIn('apartamento', str(context.exception))

    def test_resident_without_condominium_raises_error(self):
        """Testa que morador sem condomínio gera erro"""
        apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=101,
            block='A',
            tread=1
        )

        resident = Person(
            email='resident@nocondo.com',
            name='Resident No Condo',
            cpf='40404040404',
            user_type='resident',
            apartment=apartment
        )
        resident.set_password('pass123')

        with self.assertRaises(ValidationError) as context:
            resident.full_clean()
        self.assertIn('condomínio', str(context.exception))

    def test_employee_without_position_raises_error(self):
        """Testa que funcionário sem cargo gera erro"""
        employee = Person(
            email='employee@noposition.com',
            name='Employee No Position',
            cpf='50505050505',
            user_type='employee',
            condominium=self.condominium
        )
        employee.set_password('pass123')

        with self.assertRaises(ValidationError) as context:
            employee.full_clean()
        self.assertIn('cargo', str(context.exception))

    def test_employee_without_condominium_raises_error(self):
        """Testa que funcionário sem condomínio gera erro"""
        employee = Person(
            email='employee@nocondo.com',
            name='Employee No Condo',
            cpf='60606060606',
            user_type='employee',
            position='Porteiro'
        )
        employee.set_password('pass123')

        with self.assertRaises(ValidationError) as context:
            employee.full_clean()
        self.assertIn('condomínio', str(context.exception))

    def test_create_resident_successfully(self):
        """Testa criação bem-sucedida de morador"""
        apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=102,
            block='A',
            tread=1
        )

        resident = Person.objects.create_user(
            email='resident@success.com',
            name='Resident Success',
            cpf='70707070707',
            password='pass123',
            user_type='resident',
            condominium=self.condominium,
            apartment=apartment
        )
        self.assertEqual(resident.user_type, Person.UserType.RESIDENT)
        self.assertEqual(resident.apartment, apartment)

    def test_create_employee_successfully(self):
        """Testa criação bem-sucedida de funcionário"""
        employee = Person.objects.create_user(
            email='employee@success.com',
            name='Employee Success',
            cpf='80808080808',
            password='pass123',
            user_type='employee',
            condominium=self.condominium,
            position='Zelador'
        )
        self.assertEqual(employee.user_type, Person.UserType.EMPLOYEE)
        self.assertEqual(employee.position, 'Zelador')

    def test_create_admin_successfully(self):
        """Testa criação bem-sucedida de administrador"""
        admin = Person.objects.create_user(
            email='admin@success.com',
            name='Admin Success',
            cpf='90909090909',
            password='pass123',
            user_type='admin'
        )
        self.assertEqual(admin.user_type, Person.UserType.ADMIN)
        self.assertTrue(admin.is_active)

    def test_approve_person_activates_account(self):
        """Testa que approve_person ativa a conta"""
        apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=103,
            block='A',
            tread=1
        )

        resident = Person.objects.create_user(
            email='resident@approve.com',
            name='Resident Approve',
            cpf='11223344556',
            password='pass123',
            user_type='resident',
            condominium=self.condominium,
            apartment=apartment
        )

        self.assertFalse(resident.is_active)
        resident.approve_person()
        self.assertTrue(resident.is_active)

    def test_username_field_is_email(self):
        """Testa que USERNAME_FIELD é email"""
        self.assertEqual(Person.USERNAME_FIELD, 'email')

    def test_required_fields(self):
        """Testa campos obrigatórios"""
        required_fields = Person.REQUIRED_FIELDS
        self.assertIn('name', required_fields)
        self.assertIn('user_type', required_fields)
        self.assertIn('cpf', required_fields)

    def test_admin_can_manage_multiple_condominiums(self):
        """Testa que admin pode gerenciar múltiplos condomínios"""
        address2 = Address.objects.create(
            street='Rua 2',
            number=20,
            neighborhood='Centro',
            city='Cidade',
            state='ST',
            zip_code='33333333'
        )

        condominium2 = Condominium.objects.create(
            name='Condo 2',
            cnpj='22222222000111',
            address=address2,
            created_by=self.admin
        )

        self.admin.managed_condominiums.add(self.condominium, condominium2)
        self.assertEqual(self.admin.managed_condominiums.count(), 2)

    def test_registered_by_tracks_creator(self):
        """Testa que registered_by rastreia criador"""
        apartment = Apartment.objects.create(
            condominium=self.condominium,
            number=104,
            block='A',
            tread=1
        )

        resident = Person.objects.create_user(
            email='resident@tracked.com',
            name='Resident Tracked',
            cpf='22334455667',
            password='pass123',
            user_type='resident',
            condominium=self.condominium,
            apartment=apartment,
            registered_by=self.admin
        )

        self.assertEqual(resident.registered_by, self.admin)
        self.assertEqual(self.admin.registered_users.count(), 1)
