from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from .models import PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('tipo_documento', 'numero_documento', 'telefono', 'direccion', 
              'fecha_nacimiento', 'estado_socio')

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_groups', 'get_estado_socio', 'is_active')
    list_filter = ('is_active', 'is_staff', 'groups', 'perfil__estado_socio')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'perfil__numero_documento')
    ordering = ('username',)
    
    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Grupos'
    
    def get_estado_socio(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_estado_socio_display()
        return 'Sin perfil'
    get_estado_socio.short_description = 'Estado como Socio'

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_user_count')
    search_fields = ('name',)
    ordering = ('name',)
    
    def get_user_count(self, obj):
        return obj.user.count()
    get_user_count.short_description = 'Número de Usuarios'

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Re-register GroupAdmin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'numero_documento', 'tipo_documento', 'telefono', 'estado_socio', 'fecha_registro')
    list_filter = ('estado_socio', 'tipo_documento', 'fecha_registro')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'numero_documento')
    ordering = ('usuario__username',)
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
