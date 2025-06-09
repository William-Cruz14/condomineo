from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(BaseUserAdmin, ModelAdmin):
    model = Profile
    add_form = UserCreationForm
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm

    list_display = ('email', 'first_name', 'last_name', 'date_joined')
    list_filter = ('email',)