from django.contrib import admin
from unfold.admin import ModelAdmin
from .forms import PersonCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
from .models import Person

@admin.register(Person)
class PersonAdmin(BaseUserAdmin, ModelAdmin):
    ordering = ['email']
    model = Person
    add_form = PersonCreationForm
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('email', 'name', 'user_type', 'date_joined', 'last_login', 'condominium')

    fieldsets = (
        (None, {'fields': ('email', 'name', 'user_type', 'cpf', 'apartment', 'position', 'condominium', 'managed_condominiums', 'password')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'user_type', 'cpf', 'apartment', 'position', 'condominium', 'managed_condominiums', 'password1', 'password2'),
        }),
    )