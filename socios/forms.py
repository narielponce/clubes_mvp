from django import forms
from .models import Socio, TipoSocio
from usuarios.models import PerfilUsuario

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ['perfil_usuario', 'tipo_socio', 'fecha_afiliacion', 'observaciones']
        widgets = {
            'fecha_afiliacion': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['perfil_usuario'] = forms.ModelChoiceField(
            queryset=PerfilUsuario.objects.all(),
            label='Usuario',
            help_text='Seleccione el perfil de usuario que será socio'
        )
        self.fields['tipo_socio'] = forms.ModelChoiceField(
            queryset=TipoSocio.objects.all(),
            label='Tipo de Socio'
        )
        self.fields['fecha_afiliacion'].label = 'Fecha de Afiliación'
        self.fields['observaciones'].label = 'Observaciones'
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'input'})
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'select'})

    def clean_perfil_usuario(self):
        perfil = self.cleaned_data['perfil_usuario']
        # Permitir el mismo perfil si estamos editando
        if self.instance.pk:
            if hasattr(perfil, 'socio') and perfil.socio.pk != self.instance.pk:
                raise forms.ValidationError('Este usuario ya tiene un perfil de socio.')
        else:
            if hasattr(perfil, 'socio'):
                raise forms.ValidationError('Este usuario ya tiene un perfil de socio.')
        return perfil

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance
