from django.db import models
from django.utils import timezone
from usuarios.models import PerfilUsuario
from socios.models import Socio

class Dia(models.Model):
    nombre = models.CharField(max_length=10)
    
    def __str__(self):
        return self.nombre

class Horario(models.Model):
    dias = models.ManyToManyField(Dia, related_name='horarios')
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    
    def __str__(self):
        dias_str = ", ".join([dia.nombre for dia in self.dias.all()])
        return f"{dias_str} de {self.hora_inicio} a {self.hora_fin}"

class Profesor(models.Model):
    perfil_usuario = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.perfil_usuario.usuario.get_full_name()} - {self.especialidad}"

class Disciplina(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    coordinador = models.ForeignKey(PerfilUsuario, on_delete=models.PROTECT, related_name='disciplinas_coordinadas')
    lugar = models.CharField(max_length=100)
    cupo_maximo = models.IntegerField()
    costo_mensual = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)
    profesores = models.ManyToManyField(Profesor, related_name='categorias')
    horario = models.ForeignKey(Horario, on_delete=models.PROTECT)
    cupo_maximo = models.IntegerField()
    
    def __str__(self):
        return f"{self.disciplina.nombre} - {self.nombre}"

class Inscripcion(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='inscripciones')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='inscritos')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('socio', 'categoria')
        
    def __str__(self):
        return f"{self.socio.perfil_usuario.usuario.get_full_name()} - {self.categoria}"

    def save(self, *args, **kwargs):
        # Verificar si el cupo está disponible
        if self.categoria.inscritos.filter(activa=True).count() >= self.categoria.cupo_maximo:
            raise ValueError(f"La categoría {self.categoria} ha alcanzado su cupo máximo")
        super().save(*args, **kwargs)
