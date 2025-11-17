from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from users.models import Person
from .models import Address, Condominium, Apartment


class CondominiumModelTests(TestCase):
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
        condo = Condominium.objects.create(
            name='Residencial Primavera',
            cnpj='12345678901234',
            address=self.address,
            created_by=self.creator
        )

        self.assertEqual(len(condo.code_condominium), 8)
        self.assertTrue(condo.code_condominium.isupper())

    def test_str_returns_human_readable_value(self):
        condo = Condominium.objects.create(
            name='Residencial Outono',
            cnpj='22345678901234',
            address=self.address,
            created_by=self.creator
        )

        expected = f'{condo.name} ({condo.code_condominium})'
        self.assertEqual(str(condo), expected)


class ApartmentModelTests(TestCase):
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
        cls.condominium = Condominium.objects.create(
            name='Residencial Verão',
            cnpj='32345678901234',
            address=cls.address,
            created_by=cls.creator
        )

    def test_apartment_number_must_be_positive(self):
        with self.assertRaises(ValidationError):
            apartment = Apartment(
                number=0,
                block="A",
                tread=1,
                condominium=self.condominium,
            )
            apartment.full_clean()


    def test_str_returns_human_readable_value(self):
        apartment = Apartment.objects.create(
            number=101,
            tread=1,
            block="S",
            condominium=self.condominium,
        )

        expected = f'Apartamento {apartment.number} - Bloco {apartment.block} - Piso {apartment.tread} ({self.condominium.name})'
        self.assertEqual(str(apartment), expected)