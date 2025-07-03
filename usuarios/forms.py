from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import PerfilUsuario

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # Si es una edición
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False
        else:  # Si es creación
            self.fields['password'].required = True
            self.fields['confirm_password'].required = True
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['tipo_documento', 'numero_documento', 'telefono', 'direccion', 'fecha_nacimiento', 'estado_socio']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'input'}),
            'telefono': forms.TextInput(attrs={'class': 'input'}),
            'direccion': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'estado_socio': forms.Select(attrs={'class': 'select'}),
        }
        labels = {
            'estado_socio': 'Estado como Socio',
        }
        help_texts = {
            'estado_socio': 'Estado específico del usuario como socio del club',
        }
    
    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')
        if self.instance.pk:  # Si es una edición
            # Excluir el usuario actual de la validación de unicidad
            if PerfilUsuario.objects.filter(numero_documento=numero_documento).exclude(usuario=self.instance.usuario).exists():
                raise forms.ValidationError("Ya existe un usuario con este número de documento.")
        else:  # Si es creación
            if PerfilUsuario.objects.filter(numero_documento=numero_documento).exists():
                raise forms.ValidationError("Ya existe un usuario con este número de documento.")
        return numero_documento

class GrupoForm(forms.Form):
    nombre = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nombre del grupo'})
    )
    
    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        from django.contrib.auth.models import Group
        if Group.objects.filter(name=nombre).exists():
            raise forms.ValidationError("Ya existe un grupo con este nombre.")
        return nombre

# Formularios específicos para mi_perfil (sin campos sensibles)
class MiPerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['tipo_documento', 'numero_documento', 'telefono', 'direccion', 'fecha_nacimiento']
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'select'}),
            'numero_documento': forms.TextInput(attrs={'class': 'input'}),
            'telefono': forms.TextInput(attrs={'class': 'input'}),
            'direccion': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        }
    
    def clean_numero_documento(self):
        numero_documento = self.cleaned_data.get('numero_documento')
        if self.instance.pk:  # Si es una edición
            # Excluir el usuario actual de la validación de unicidad
            if PerfilUsuario.objects.filter(numero_documento=numero_documento).exclude(usuario=self.instance.usuario).exists():
                raise forms.ValidationError("Ya existe un usuario con este número de documento.")
        else:  # Si es creación
            if PerfilUsuario.objects.filter(numero_documento=numero_documento).exists():
                raise forms.ValidationError("Ya existe un usuario con este número de documento.")
        return numero_documento

class MiUsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input'}),
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].required = False
        self.fields['confirm_password'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data 