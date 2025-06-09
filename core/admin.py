from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Apartment,Visitor, Reservation, Communication, Finance, Vehicle, Orders, Visit, Person
from .forms import VisitorForm, CommunicationForm, ReservationForm, FinanceForm, VehicleForm, ApartmentForm, OrdersForm

admin.site.unregister(Group)

# Cadastro do modelo 'Apartamento' no site de administração, para que os síndicos e administradores possam gerenciar
# os Apartamentos.

@admin.register(Apartment)
class ApartmentAdmin(ModelAdmin):
    model = Apartment
    form = ApartmentForm
    list_display = ('number', 'block', 'tread', 'occupation')
    search_fields = ('number', 'block')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)


# Cadastro do modelo 'CustomUser' no site de administração, para que os síndicos e administradores possam gerenciar
# os Usuários.
@admin.register(Person)
class CustomUserAdmin(ModelAdmin):
    list_display = ('id', 'name', 'document', 'user_type',)
    list_filter = ('user_type',)
    search_fields = ('name', 'document')
    ordering = ('name',)

# Cadastro do modelo 'Visitante' no site de administração, para que os moradores, síndicos e administradores possam gerenciar
# os Visitantes.
@admin.register(Visitor)
class VisitorAdmin(ModelAdmin):
    list_display = ('name', 'document', 'registered_by')
    search_fields = ('name', 'document', 'registered_by__name')
    form = VisitorForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo 'Reserva' no site de administração, para que os moradores, síndicos e administradores possam gerenciar
# as reservas.
@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    list_display = ('id','resident', 'space', 'start_time', 'end_time')
    search_fields = ('resident__name', 'space',)
    ordering = ('id',)
    form = ReservationForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.resident = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo 'Comunicação' no site de administração, para que os síndicos e administradores possam gerenciar
# as comunicações.
@admin.register(Communication)
class CommunicationAdmin(ModelAdmin):
    list_display = ('sender', 'subject', 'sent_at')
    search_fields = ('subject', 'sent_at')
    form = CommunicationForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.sender = request.user
        super().save_model(request, obj, form, change)



@admin.register(Finance)
class FinanceAdmin(ModelAdmin):
    list_display = ('creator', 'value', 'description', 'date', 'document')
    search_fields = ('date',)
    ordering = ('date',)
    form = FinanceForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.creator = request.user
        super().save_model(request, obj, form, change)


@admin.register(Vehicle)
class VehicleAdmin(ModelAdmin):
    list_display = ('plate', 'model', 'color', 'garage', 'owner')
    search_fields = ('plate', 'model', 'color', 'garage')
    form = VehicleForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo 'Grupo' no site de administração, para que os síndicos e administradores possam gerenciar
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

@admin.register(Orders)
class OrdersAdmin(ModelAdmin):
    list_display = ('id', 'order_code', 'status', 'order_date', 'owner', 'registered_by')
    search_fields = ('owner__document', 'order_date')
    ordering = ('-order_date',)
    form = OrdersForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)



@admin.register(Visit)
class VisitAdmin(ModelAdmin):
    list_display = ('visitor', 'apartment', 'entry_date', 'exit_date')
    search_fields = ('visitor__name', 'apartment__number',)
    ordering = ('-apartment',)
