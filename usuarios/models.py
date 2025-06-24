from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class PerfilUsuario(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'DNI'),
        ('CE', 'Carné de Extranjería'),
        ('PAS', 'Pasaporte'),
    ]
    
    ESTADO_SOCIO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
        ('PENDIENTE', 'Pendiente de Aprobación'),
        ('RETIRADO', 'Retirado'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_documento = models.CharField(max_length=3, choices=TIPO_DOCUMENTO_CHOICES, default='DNI')
    numero_documento = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    estado_socio = models.CharField(max_length=10, choices=ESTADO_SOCIO_CHOICES, default='ACTIVO', 
                                   verbose_name='Estado como Socio')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'
    
    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.numero_documento}"
    
    @property
    def esta_activo_sistema(self):
        """Retorna True si el usuario está activo tanto en el sistema como socio"""
        return self.usuario.is_active and self.estado_socio == 'ACTIVO'
    
    @property
    def estado_completo(self):
        """Retorna el estado completo del usuario"""
        if not self.usuario.is_active:
            return "Cuenta Deshabilitada"
        return self.get_estado_socio_display()

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
