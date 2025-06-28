from django import forms
from django.contrib.auth.models import Group, User
from usuarios.models import PerfilUsuario
from .models import Disciplina, Categoria, Horario, Dia, Inscripcion
from socios.models import Socio

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
        fields = ['disciplina', 'nombre', 'profesores', 'horario', 'cupo_maximo', 'especialidad']
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

class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = ['socio', 'categoria']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo socios activos (usuario activo y estado_socio = 'ACTIVO')
        self.fields['socio'].queryset = Socio.objects.filter(
            perfil_usuario__usuario__is_active=True,
            perfil_usuario__estado_socio='ACTIVO'
        ).select_related('perfil_usuario__usuario')
        
        # Filtrar solo categorías activas
        self.fields['categoria'].queryset = Categoria.objects.filter(
            disciplina__activa=True
        ).select_related('disciplina')
        
        # Personalizar las etiquetas
        self.fields['socio'].label = 'Socio'
        self.fields['categoria'].label = 'Categoría'
        
        # Agregar placeholders
        self.fields['socio'].widget.attrs.update({'class': 'input'})
        self.fields['categoria'].widget.attrs.update({'class': 'input'})
    
    def clean(self):
        cleaned_data = super().clean()
        socio = cleaned_data.get('socio')
        categoria = cleaned_data.get('categoria')
        
        if socio and categoria:
            # Verificar si ya existe una inscripción activa
            if Inscripcion.objects.filter(socio=socio, categoria=categoria, activa=True).exists():
                raise forms.ValidationError(
                    f"El socio {socio} ya está inscrito en la categoría {categoria}"
                )
            
            # Verificar cupo disponible
            inscritos_activos = categoria.inscritos.filter(activa=True).count()
            if inscritos_activos >= categoria.cupo_maximo:
                raise forms.ValidationError(
                    f"La categoría {categoria} ha alcanzado su cupo máximo ({categoria.cupo_maximo} personas)"
                )
        
        return cleaned_data
