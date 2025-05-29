from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.forms import ModelForm, Select, ModelChoiceField
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.hashers import make_password
from .models import Product, InventoryMovement, CurrentStock, PredictorStock

# Roles disponibles
AVAILABLE_ROLES = ['Administrador', 'Lectura']

# Desregistrar el modelo Group ya que no lo usaremos directamente
admin.site.unregister(Group)

class CustomUserCreationForm(UserCreationForm):
    """Formulario para crear nuevos usuarios con grupo"""
    group = ModelChoiceField(
        queryset=Group.objects.filter(name__in=AVAILABLE_ROLES),
        required=True,
        label='Permiso',
        widget=Select(),
        help_text='Seleccione el nivel de permiso para este usuario'
    )

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'group')

    def save(self, commit=True):
        if not commit:
            return super().save(commit=False)
        
        # Crear el usuario usando create_user para manejar correctamente la contraseña
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            email=self.cleaned_data.get('email', ''),
            first_name=self.cleaned_data.get('first_name', ''),
            last_name=self.cleaned_data.get('last_name', '')
        )
        
        # Configurar permisos básicos
        user.is_active = True
        user.is_staff = True  # Necesario para acceder al admin
        user.is_superuser = False
        user.save()

        # Asignar grupo y permisos específicos
        if self.cleaned_data.get('group'):
            group = self.cleaned_data['group']
            user.groups.add(group)
            # Si es grupo de lectura, quitar is_staff
            if group.name == 'Lectura':
                user.is_staff = False
            user.save()
        
        return user

class CustomUserChangeForm(UserChangeForm):
    """Formulario personalizado para manejar el campo de grupos como un select simple"""
    group = ModelChoiceField(
        queryset=Group.objects.filter(name__in=AVAILABLE_ROLES),
        required=True,
        label='Permiso',
        widget=Select(),
        help_text='Seleccione el nivel de permiso para este usuario'
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['group'].initial = self.instance.groups.first()

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Simplificar la lista de campos mostrados
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_active']
    
    def get_role(self, obj):
        """Obtener el primer rol del usuario (ya que ahora solo tendrá uno)"""
        return obj.groups.first().name if obj.groups.exists() else '-'
    get_role.short_description = 'Permiso'
    
    # Definir los fieldsets personalizados
    fieldsets = [
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permisos', {'fields': ('group', 'is_active')}),
    ]
    
    # Fieldsets para añadir usuarios
    add_fieldsets = [
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'group'),
        }),
    ]

    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo usuario
            if isinstance(form, CustomUserCreationForm):
                # Dejamos que el formulario maneje todo
                return form.save()
        
        # Si es una edición
        super().save_model(request, obj, form, change)
        selected_group = form.cleaned_data.get('group')
        if selected_group:
            obj.groups.clear()
            obj.groups.add(selected_group)
            # Actualizar is_staff según el grupo
            obj.is_staff = (selected_group.name == 'Administrador')
            obj.save()

# Registrar el modelo Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'product_name', 'category', 'cost', 'sale_price', 'active')
    list_filter = ('category', 'active')
    search_fields = ('product_id', 'product_name', 'sku')

# Registrar el modelo InventoryMovement
@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
    list_display = ('movement_id', 'date', 'product', 'movement_type', 'quantity', 'order_id')
    list_filter = ('movement_type', 'date')
    search_fields = ('movement_id', 'order_id', 'product__product_name')

# Registrar el modelo CurrentStock
@admin.register(CurrentStock)
class CurrentStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'last_updated', 'total_inventory_cost')
    search_fields = ('product__product_name',)

@admin.register(PredictorStock)
class PredictorStockAdmin(admin.ModelAdmin):
    list_display = ('date', 'product', 'units_sold', 'avg_sale_price', 'promotion_active', 'special_event')
    list_filter = ('date', 'promotion_active')
    search_fields = ('product__product_name', 'special_event')

# Desregistrar y volver a registrar User con nuestro CustomUserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
