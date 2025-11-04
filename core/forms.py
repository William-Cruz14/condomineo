from django import forms
from .models import (
    Visitor, Reservation, Finance, Vehicle, Apartment,
    Order, Condominium, Notice, Communication
)


class CondominiumForm(forms.ModelForm):
    class Meta:
        model = Condominium
        fields = ['name', 'cnpj', 'address' ]


# Definindo o formulário de reserva
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['space', 'resident', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['condominium', 'number', 'block', 'tread', 'occupation', 'exit_date']

# Definindo o formulário de visitante
class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['condominium', 'name', 'cpf', 'telephone']

class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['condominium', 'value', 'description', 'document']


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['condominium', 'plate', 'model', 'color', 'owner']



class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_code','status', 'owner', 'signature_image']


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'condominium', 'file_complement', 'author']


class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = '__all__'