from django.db import models
from django.contrib.auth.models import User
from socios.models import Socio
from disciplinas.models import Disciplina, Categoria
from django.core.validators import MinValueValidator
from decimal import Decimal

class Cuenta(models.Model):
    TIPO_CUENTA_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('BANCO', 'Banco'),
        ('BILLETERA_VIRTUAL', 'Billetera Virtual'),
    ]
    
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CUENTA_CHOICES)
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'
        ordering = ['tipo', 'nombre']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

class Deuda(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADA', 'Pagada'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='deudas')
    fecha_generacion = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='PENDIENTE')
    observaciones = models.TextField(blank=True, null=True)
    generada_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='deudas_generadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Deuda'
        verbose_name_plural = 'Deudas'
        ordering = ['-fecha_generacion']
    
    def __str__(self):
        return f"Deuda de {self.socio} - {self.fecha_generacion} - ${self.monto_total}"
    
    def calcular_total(self):
        """Calcula el total sumando todos los items de la deuda"""
        total = sum(item.monto for item in self.items.all())
        self.monto_total = total
        self.save()
        return total

class ItemDeuda(models.Model):
    TIPO_ITEM_CHOICES = [
        ('CUOTA_SOCIETARIA', 'Cuota Societaria'),
        ('CUOTA_DISCIPLINA', 'Cuota por Disciplina'),
        ('OTRO', 'Otro'),
    ]
    
    deuda = models.ForeignKey(Deuda, on_delete=models.CASCADE, related_name='items')
    tipo = models.CharField(max_length=20, choices=TIPO_ITEM_CHOICES)
    descripcion = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    disciplina = models.ForeignKey(Disciplina, on_delete=models.SET_NULL, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Item de Deuda'
        verbose_name_plural = 'Items de Deuda'
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.descripcion} - ${self.monto}"

class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('EGRESO', 'Egreso'),
    ]
    
    CATEGORIA_CHOICES = [
        ('CUOTAS', 'Cuotas de Socios'),
        ('INSCRIPCIONES', 'Inscripciones'),
        ('EVENTOS', 'Eventos'),
        ('EQUIPAMIENTO', 'Equipamiento'),
        ('MANTENIMIENTO', 'Mantenimiento'),
        ('SERVICIOS', 'Servicios'),
        ('SALARIOS', 'Salarios'),
        ('OTRO', 'Otro'),
    ]
    
    cuenta = models.ForeignKey(Cuenta, on_delete=models.PROTECT, related_name='transacciones')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    descripcion = models.TextField()
    fecha = models.DateField()
    referencia = models.CharField(max_length=100, blank=True, null=True)
    registrado_por = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transacciones_registradas')
    deuda_relacionada = models.ForeignKey(Deuda, on_delete=models.SET_NULL, null=True, blank=True, related_name='transacciones')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transacción'
        verbose_name_plural = 'Transacciones'
        ordering = ['-fecha', '-fecha_creacion']
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cuenta} - ${self.monto} - {self.fecha}"
    
    def save(self, *args, **kwargs):
        # Actualizar saldo de la cuenta
        if self.pk:  # Si es una actualización
            old_transaction = Transaccion.objects.get(pk=self.pk)
            if old_transaction.tipo == 'INGRESO':
                self.cuenta.saldo_actual -= old_transaction.monto
            else:
                self.cuenta.saldo_actual += old_transaction.monto
        
        # Aplicar la nueva transacción
        if self.tipo == 'INGRESO':
            self.cuenta.saldo_actual += self.monto
        else:
            self.cuenta.saldo_actual -= self.monto
        
        self.cuenta.save()
        super().save(*args, **kwargs)

class Comprobante(models.Model):
    TIPO_CHOICES = [
        ('FACTURA', 'Factura'),
        ('RECIBO', 'Recibo'),
        ('TICKET', 'Ticket'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('OTRO', 'Otro'),
    ]
    
    transaccion = models.ForeignKey(Transaccion, on_delete=models.CASCADE, related_name='comprobantes')
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    numero = models.CharField(max_length=50)
    archivo = models.FileField(upload_to='comprobantes/', blank=True, null=True)
    fecha_emision = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comprobante'
        verbose_name_plural = 'Comprobantes'
        ordering = ['-fecha_emision']
    
    def __str__(self):
        return f"{self.get_tipo_display()} {self.numero} - ${self.monto}"
