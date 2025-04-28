from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, Visitor, Reservation, Communication, Finance

# Definindo o formulário de criação de usuário personalizado
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'document', 'user_type', 'telephone')
        labels = {'username': 'Username/E-mail'}

# Definindo o formulário de alteração de usuário personalizado
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('name', 'document', 'user_type', 'telephone', 'is_staff', 'is_superuser', 'is_active')

# Definindo o formulário de visitante
class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = ['recipient', 'subject', 'message']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

# Definindo o formulário de reserva
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['space', 'date', 'time', 'end_time']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

# Definindo o formulário de visitante
class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['name', 'document', 'telephone', 'apartment']

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