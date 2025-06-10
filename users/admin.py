from django.contrib import admin
from unfold.admin import ModelAdmin
from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(BaseUserAdmin, ModelAdmin):
    model = Profile
    add_form = CustomUserCreationForm
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('email', 'name', 'date_joined')
    list_filter = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'name', 'password')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )