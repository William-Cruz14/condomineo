from unfold.forms import UserCreationForm as UnfoldUserCreationForm
from .models import Person
from django import forms

class PersonCreationForm(UnfoldUserCreationForm):
    class Meta:
        model = Person
        fields = ('email', 'name', 'user_type', 'cpf', 'apartment', 'position', 'condominium', 'managed_condominiums')

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('name'):
            cleaned_data['name'] = cleaned_data['name'].title()

        cpf = cleaned_data.get('cpf')
        if cpf and Person.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError("Um usuário com este CPF já existe.")

        managed_condominiums = cleaned_data.get('managed_condominiums')
        if cleaned_data.get('user_type') == Person.UserType.ADMIN:
            if not managed_condominiums or len(managed_condominiums) == 0:
                raise forms.ValidationError("Pelo menos um condomínio deve ser selecionado para gerenciamento.")

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['apartment'].empty_label = "Selecione um apartamento"
        self.fields['managed_condominiums'].help_text = "Selecione os condomínios que este usuário pode gerenciar (apenas para administradores)."
