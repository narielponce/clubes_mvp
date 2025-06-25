from django import forms
from .models import Disciplina, Categoria, Profesor, Horario, Dia

class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nombre', 'descripcion', 'coordinador', 'lugar', 'cupo_maximo', 'costo_mensual']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'lugar': forms.TextInput(attrs={'class': 'input'}),
            'cupo_maximo': forms.NumberInput(attrs={'class': 'input'}),
            'costo_mensual': forms.NumberInput(attrs={'class': 'input'})
        }

class CategoriaForm(forms.ModelForm):
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

class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ['perfil_usuario', 'especialidad']
        widgets = {
            'perfil_usuario': forms.Select(attrs={'class': 'select'}),
            'especialidad': forms.TextInput(attrs={'class': 'input'})
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
