from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Apartment, CustomUser, Visitor, Reservation, Communication, Finance
from .forms import CustomUserCreationForm, VisitorForm, CommunicationForm, ReservationForm, CustomUserChangeForm, \
    FinanceForm


# Cadastro do modelo "Apartamento" no site de administração, para que os síndicos e administradores possam gerenciar
# os Apartamentos.
@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('number', 'block', 'floor')
    search_fields = ('number', 'block')

# Cadastro do modelo "CustomUser" no site de administração, para que os síndicos e administradores possam gerenciar
# os Usuários.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ('email', 'name','user_type', 'is_staff', 'apartment', 'date_joined', 'last_login')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    search_fields = ('email', 'name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('name', 'document', 'telephone', 'user_type', 'apartment')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'document', 'telephone', 'user_type', 'apartment', 'password1', 'password2'),
        }),
    )

# Cadastro do modelo "Visitante" no site de administração, para que os moradores, síndicos e administradores possam gerenciar
# os Visitantes.
@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'document', 'apartment', 'registered_by', 'entry_date')
    search_fields = ('name', 'document', 'apartment__number', 'registered_by__name')
    form = VisitorForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        return form

    def has_module_permission(self, request):
        return request.user.has_perm('core.view_visitor')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo "Reserva" no site de administração, para que os moradores, síndicos e administradores possam gerenciar
# as reservas.
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id','resident', 'space', 'date', 'time', 'end_time')
    search_fields = ('resident__name', 'space', 'date')
    ordering = ('id',)
    form = ReservationForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        return form

    def has_module_permission(self, request):
        return request.user.has_perm('core.view_reservation')


    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.resident = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo "Comunicação" no site de administração, para que os síndicos e administradores possam gerenciar
# as comunicações.
@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'subject', 'to_all_moradores', 'sent_at')
    search_fields = ('sender__name', 'recipient__name', 'subject')
    form = CommunicationForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.sender = request.user
        super().save_model(request, obj, form, change)



@admin.register(Finance)
class FinanceAdmin(admin.ModelAdmin):
    list_display = ('creator', 'value', 'description', 'date', 'document')
    search_fields = ('date',)
    ordering = ('date',)
    form = FinanceForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        return form

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.creator = request.user
        super().save_model(request, obj, form, change)