from django import forms
from django.contrib.auth.models import Group, User
from usuarios.models import PerfilUsuario
from .models import Disciplina, Categoria, Horario, Dia

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nombre', 'descripcion', 'coordinador', 'lugar', 'costo_mensual', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'lugar': forms.TextInput(attrs={'class': 'input'}),
            'costo_mensual': forms.NumberInput(attrs={'class': 'input'})
        }

class CategoriaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar profesores por grupo
        profesores_group = Group.objects.get(name='Profesor')
        # Primero obtenemos los usuarios que están en el grupo Profesor
        usuarios_profesores = User.objects.filter(groups=profesores_group)
        # Luego filtramos los perfiles de usuario basados en estos usuarios
        self.fields['profesores'].queryset = PerfilUsuario.objects.filter(usuario__in=usuarios_profesores)
        # Estilizar el select de profesores
        self.fields['profesores'].widget.attrs.update({
            'class': 'select is-multiple',
            'size': '5',  # Altura del select
            'style': 'height: 200px;'  # Altura fija
        })
        # Estilizar el select de horario
        self.fields['horario'].widget.attrs.update({
            'class': 'select',
            'style': 'height: 50px;'  # Altura reducida
        })
        # Asegurar que el queryset de horarios no esté vacío
        if not self.fields['horario'].queryset.exists():
            self.fields['horario'].queryset = Horario.objects.all()

    class Meta:
        model = Categoria
        fields = ['disciplina', 'nombre', 'profesores', 'horario', 'cupo_maximo']
        widgets = {
            'disciplina': forms.Select(attrs={'class': 'select'}),
            'nombre': forms.TextInput(attrs={'class': 'input'}),
            'profesores': forms.SelectMultiple(attrs={'class': 'select'}),
            'horario': forms.Select(attrs={'class': 'select'}),
            'cupo_maximo': forms.NumberInput(attrs={'class': 'input'})
        }

class HorarioForm(forms.ModelForm):
    class Meta:
        model = Horario
        fields = ['dias', 'hora_inicio', 'hora_fin']
        widgets = {
            'dias': forms.SelectMultiple(attrs={'class': 'select'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'input', 'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'class': 'input', 'type': 'time'})
        }

class DiaForm(forms.ModelForm):
    class Meta:
        model = Dia
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input'})
        }
