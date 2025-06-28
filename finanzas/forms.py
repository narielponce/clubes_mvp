from django import forms
from .models import Cuenta, Deuda, ItemDeuda, Transaccion, Comprobante
from socios.models import Socio
from disciplinas.models import Disciplina, Categoria

class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = ['nombre', 'tipo', 'saldo_actual', 'descripcion', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input'}),
            'tipo': forms.Select(attrs={'class': 'select'}),
            'saldo_actual': forms.NumberInput(attrs={'class': 'input'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'activa': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }

class DeudaForm(forms.ModelForm):
    class Meta:
        model = Deuda
        fields = ['socio', 'fecha_vencimiento', 'observaciones']
        widgets = {
            'socio': forms.Select(attrs={'class': 'select'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
        }

class ItemDeudaForm(forms.ModelForm):
    class Meta:
        model = ItemDeuda
        fields = ['tipo', 'descripcion', 'monto', 'disciplina', 'categoria']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'select'}),
            'descripcion': forms.TextInput(attrs={'class': 'input'}),
            'monto': forms.NumberInput(attrs={'class': 'input', 'step': '0.01', 'min': '0.01'}),
            'disciplina': forms.Select(attrs={'class': 'select'}),
            'categoria': forms.Select(attrs={'class': 'select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer disciplina y categoria opcionales
        self.fields['disciplina'].required = False
        self.fields['categoria'].required = False
        
        # Filtrar categorías basadas en la disciplina seleccionada
        if 'disciplina' in self.data:
            try:
                disciplina_id = int(self.data.get('disciplina'))
                self.fields['categoria'].queryset = Categoria.objects.filter(disciplina_id=disciplina_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.disciplina:
            self.fields['categoria'].queryset = self.instance.disciplina.categorias.all()

class TransaccionForm(forms.ModelForm):
    socio_pago = forms.ModelChoiceField(
        queryset=Socio.objects.all(),
        required=False,
        empty_label="Seleccionar socio...",
        label="Socio (para cuotas)",
        help_text="Selecciona el socio al cual imputar el pago"
    )
    
    class Meta:
        model = Transaccion
        fields = ['cuenta', 'tipo', 'categoria', 'monto', 'descripcion', 'fecha', 'referencia', 'deuda_relacionada']
        widgets = {
            'cuenta': forms.Select(attrs={'class': 'select'}),
            'tipo': forms.Select(attrs={'class': 'select'}),
            'categoria': forms.Select(attrs={'class': 'select'}),
            'monto': forms.NumberInput(attrs={'class': 'input', 'step': '0.01', 'min': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
            'fecha': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'referencia': forms.TextInput(attrs={'class': 'input'}),
            'deuda_relacionada': forms.Select(attrs={'class': 'select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer deuda_relacionada opcional
        self.fields['deuda_relacionada'].required = False
        # Filtrar solo deudas pendientes
        self.fields['deuda_relacionada'].queryset = Deuda.objects.filter(estado='PENDIENTE')
        
        # Configurar el campo socio_pago sin estilos inline
        self.fields['socio_pago'].widget.attrs.update({
            'class': 'select'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        tipo = cleaned_data.get('tipo')
        socio_pago = cleaned_data.get('socio_pago')
        
        # Si la categoría es CUOTAS Y el tipo es INGRESO, el socio es obligatorio
        if categoria == 'CUOTAS' and tipo == 'INGRESO' and not socio_pago:
            self.add_error('socio_pago', 'Debe seleccionar un socio cuando la categoría es "Cuotas de Socios" y el tipo es "Ingreso"')
        
        return cleaned_data

class ComprobanteForm(forms.ModelForm):
    class Meta:
        model = Comprobante
        fields = ['tipo', 'numero', 'archivo', 'fecha_emision', 'monto', 'descripcion']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'select'}),
            'numero': forms.TextInput(attrs={'class': 'input'}),
            'archivo': forms.FileInput(attrs={'class': 'file-input'}),
            'fecha_emision': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'monto': forms.NumberInput(attrs={'class': 'input', 'step': '0.01', 'min': '0.01'}),
            'descripcion': forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
        }

# Formulario para generar deudas masivamente
class GenerarDeudasForm(forms.Form):
    socios = forms.ModelMultipleChoiceField(
        queryset=Socio.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Seleccionar Socios'
    )
    fecha_vencimiento = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        label='Fecha de Vencimiento'
    )
    cuota_societaria = forms.DecimalField(
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'input', 'step': '0.01', 'min': '0'}),
        label='Cuota Societaria',
        required=False,
        initial=0
    )
    incluir_disciplinas = forms.BooleanField(
        required=False,
        initial=True,
        label='Incluir cuotas de disciplinas'
    )
    observaciones = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'textarea', 'rows': 3}),
        required=False,
        label='Observaciones'
    ) 