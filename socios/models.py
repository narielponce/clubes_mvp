from django.db import models
from usuarios.models import PerfilUsuario
from django.db.models.signals import post_save
from django.dispatch import receiver

class TipoSocio(models.Model):
    TIPO_SOCIO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('ADHERENTE', 'Adherente'),
        ('INFANTIL', 'Infantil'),
        ('HONORARIO', 'Honorario'),
    ]
    
    nombre = models.CharField(max_length=10, choices=TIPO_SOCIO_CHOICES, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Tipo de Socio'
        verbose_name_plural = 'Tipos de Socios'
        default_manager_name = 'objects'
    
    def __str__(self):
        return self.nombre

class Socio(models.Model):
    perfil_usuario = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE, related_name='socio', null=True, blank=True)
    tipo_socio = models.ForeignKey(TipoSocio, on_delete=models.PROTECT)
    fecha_afiliacion = models.DateField()
    observaciones = models.TextField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Socio'
        verbose_name_plural = 'Socios'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        if self.perfil_usuario:
            return f"{self.perfil_usuario.usuario.get_full_name()} - {self.tipo_socio}"
        return f"Socio sin perfil - {self.tipo_socio}"
    
    @property
    def esta_activo(self):
        if self.perfil_usuario:
            return self.perfil_usuario.esta_activo_sistema
        return False
    
    @property
    def tiempo_socio(self):
        from datetime import date
        import datetime
        if not self.fecha_afiliacion:
            return "Fecha de afiliación no establecida"
        dias = (datetime.date.today() - self.fecha_afiliacion).days
        if dias < 30:
            return f"{dias} días"
        elif dias < 365:
            meses = dias // 30
            return f"{meses} meses"
        else:
            años = dias // 365
            return f"{años} años"

@receiver(post_save, sender=PerfilUsuario)
def crear_socio(sender, instance, created, **kwargs):
    if created:
        # Crear un tipo de socio activo si no existe
        tipo_socio, _ = TipoSocio.objects.get_or_create(nombre='ACTIVO')
        # No crear socio automáticamente, se hace manualmente
        pass

@receiver(post_save, sender=PerfilUsuario)
def guardar_socio(sender, instance, **kwargs):
    if hasattr(instance, 'socio'):
        instance.socio.save()
