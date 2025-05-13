from django import forms
from .models import Visitor, Reservation, Communication, Finance, Vehicle, Apartment, Orders


# Definindo o formulário de visitante
class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['recipients', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

# Definindo o formulário de reserva
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['space', 'time', 'end_time']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['number', 'block', 'tread','residents', 'occupation','exit_date']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

# Definindo o formulário de visitante
class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['name', 'document', 'telephone', 'visiting','observation']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['value', 'description', 'document']


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['plate', 'model', 'color', 'garage', 'owner']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class OrdersForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['order_code','status', 'owner', 'signature_image']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)