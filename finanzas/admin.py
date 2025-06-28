from django.contrib import admin
from .models import Cuenta, Deuda, ItemDeuda, Transaccion, Comprobante

@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'tipo', 'saldo_actual', 'activa', 'fecha_creacion']
    list_filter = ['tipo', 'activa', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    list_editable = ['activa']

class ItemDeudaInline(admin.TabularInline):
    model = ItemDeuda
    extra = 1
    fields = ['tipo', 'descripcion', 'monto', 'disciplina', 'categoria']

@admin.register(Deuda)
class DeudaAdmin(admin.ModelAdmin):
    list_display = ['socio', 'fecha_generacion', 'fecha_vencimiento', 'monto_total', 'estado', 'generada_por']
    list_filter = ['estado', 'fecha_generacion', 'fecha_vencimiento', 'generada_por']
    search_fields = ['socio__nombre', 'socio__apellido', 'observaciones']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion', 'monto_total']
    date_hierarchy = 'fecha_generacion'
    inlines = [ItemDeudaInline]
    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        
        # Recalcular total de la deuda
        if instances:
            deuda = instances[0].deuda
            deuda.calcular_total()

@admin.register(ItemDeuda)
class ItemDeudaAdmin(admin.ModelAdmin):
    list_display = ['deuda', 'tipo', 'descripcion', 'monto', 'disciplina']
    list_filter = ['tipo', 'disciplina']
    search_fields = ['descripcion', 'deuda__socio__nombre']

class ComprobanteInline(admin.TabularInline):
    model = Comprobante
    extra = 1
    fields = ['tipo', 'numero', 'archivo', 'fecha_emision', 'monto']

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ['cuenta', 'tipo', 'categoria', 'monto', 'fecha', 'registrado_por']
    list_filter = ['tipo', 'categoria', 'fecha', 'cuenta', 'registrado_por']
    search_fields = ['descripcion', 'referencia', 'cuenta__nombre']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha'
    inlines = [ComprobanteInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva transacción
            obj.registrado_por = request.user
        super().save_model(request, obj, form, change)

@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ['transaccion', 'tipo', 'numero', 'fecha_emision', 'monto']
    list_filter = ['tipo', 'fecha_emision']
    search_fields = ['numero', 'descripcion', 'transaccion__descripcion']
    readonly_fields = ['fecha_creacion']
