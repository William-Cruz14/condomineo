from unfold.forms import UserCreationForm as UnfoldUserCreationForm
from .models import Person

class PersonCreationForm(UnfoldUserCreationForm):
    class Meta:
        model = Person
        fields = ('email', 'name', 'user_type', 'cpf', 'apartment', 'position', 'condominium', 'managed_condominiums')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['apartment'].empty_label = 'Selecione um apartamento'
        self.fields['managed_condominiums'].help_text = 'Selecione os condomínios que este usuário pode gerenciar (apenas para administradores).'
