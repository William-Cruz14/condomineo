from django import forms
from .models import Visitor, Reservation, Finance, Vehicle, Apartment, Order


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

    """
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
    """
# Definindo o formulário de visitante
class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['condominium', 'name', 'cpf', 'telephone']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['condominium', 'value', 'description', 'document']


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['condominium', 'plate', 'model', 'color', 'garage', 'owner']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_code','status', 'owner', 'signature_image']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)