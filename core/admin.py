from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (Apartment, Visitor, Reservation, Finance, Vehicle, Order, Visit, Condominium, Notice,
                     Communication)
from .forms import (
    VisitorForm, ReservationForm, FinanceForm, VehicleForm, ApartmentForm,
    OrderForm, CondominiumForm, NoticeForm, CommunicationForm
)

admin.site.unregister(Group)

@admin.register(Condominium)
class CondominiumAdmin(ModelAdmin):
    model = Condominium
    form = CondominiumForm
    list_display = ('name', 'cnpj', 'created_at')
    search_fields = ('name', 'number', 'cnpj')
    ordering = ('name',)
    readonly_fields = ('created_at', 'code_condominium', 'created_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Notice)
class NoticeAdmin(ModelAdmin):
    form = NoticeForm
    list_display = ('title', 'created_at', 'condominium')
    search_fields = ('title', 'content', 'condominium__name')
    list_filter = ('condominium',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'author')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo 'Apartamento' no site de administração, para que os síndicos e administradores possam gerenciar
# os Apartamentos.
@admin.register(Apartment)
class ApartmentAdmin(ModelAdmin):
    model = Apartment
    form = ApartmentForm
    list_display = ('id', 'number', 'block', 'tread', 'occupation', 'condominium')
    search_fields = ('number', 'block', 'condominium__name')
    readonly_fields = ('exit_date', 'entry_date')
    list_filter = ('condominium', 'occupation')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 'admin':
            return qs.filter(condominium__in=request.user.managed_condominiums.all())
        if request.user.apartment:
            return qs.filter(condominium=request.user.apartment.condominium)
        return qs.none()

# Cadastro do modelo 'Visitante' no site de administração, para que os moradores, síndicos e administradores possam gerenciar
# os Visitantes.
@admin.register(Visitor)
class VisitorAdmin(ModelAdmin):
    list_display = ('name', 'cpf', 'condominium', 'registered_by')
    search_fields = ('name', 'cpf', 'registered_by__name')
    list_filter = ('condominium',)
    form = VisitorForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 'admin':
            return qs.filter(condominium__in=request.user.managed_condominiums.all())
        if request.user.apartment:
            return qs.filter(condominium=request.user.apartment.condominium)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo 'Reserva' no site de administração, para que os moradores, síndicos e administradores possam gerenciar
# as reservas.
@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    list_display = ('id', 'resident', 'space', 'start_time', 'end_time')
    search_fields = ('resident__name', 'space',)
    form = ReservationForm

    def save_model(self, request, obj, form, change):
        if not change:
            obj.resident = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo 'Comunicação' no site de administração, para que os síndicos e administradores possam gerenciar
# as comunicações.

@admin.register(Finance)
class FinanceAdmin(ModelAdmin):
    list_display = ('creator', 'value', 'description', 'date', 'document', 'condominium')
    search_fields = ('date',)
    list_filter = ('condominium',)
    ordering = ('date',)
    form = FinanceForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 'admin':
            return qs.filter(condominium__in=request.user.managed_condominiums.all())
        if request.user.apartment:
            return qs.filter(condominium=request.user.apartment.condominium)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:
            obj.creator = request.user
        super().save_model(request, obj, form, change)

@admin.register(Vehicle)
class VehicleAdmin(ModelAdmin):
    list_display = ('plate', 'model', 'color', 'garage', 'owner', 'condominium')
    search_fields = ('plate', 'model', 'color', 'garage')
    list_filter = ('condominium',)
    form = VehicleForm

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.user_type == 'admin':
            return qs.filter(condominium__in=request.user.managed_condominiums.all())
        if request.user.apartment:
            return qs.filter(condominium=request.user.apartment.condominium)
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)

# Cadastro do modelo 'Grupo' no site de administração, para que os síndicos e administradores possam gerenciar
@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ('id', 'order_code', 'status', 'order_date', 'owner', 'registered_by')
    search_fields = ('owner__document', 'order_date')
    ordering = ('-order_date',)
    form = OrderForm

    def save_model(self, request, obj, form, change):
        if not change:
            obj.registered_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Visit)
class VisitAdmin(ModelAdmin):
    list_display = ('visitor', 'apartment', 'entry_date', 'exit_date')
    search_fields = ('visitor__name', 'apartment__number',)
    ordering = ('-apartment',)

@admin.register(Communication)
class CommunicationAdmin(ModelAdmin):

    form = CommunicationForm
    list_display = ('title', 'created_at', 'condominium')
    list_filter = ('condominium',)
    search_fields = ('title', 'condominium__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'sender')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.sender = request.user
        super().save_model(request, obj, form, change)