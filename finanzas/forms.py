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
        # Filtrar solo deudas pendientes o vencidas
        self.fields['deuda_relacionada'].queryset = Deuda.objects.filter(estado__in=['PENDIENTE', 'VENCIDA'])

    def clean(self):
        cleaned_data = super().clean()
        # Si la categoría es CUOTAS Y el tipo es INGRESO, la deuda es obligatoria
        categoria = cleaned_data.get('categoria')
        tipo = cleaned_data.get('tipo')
        deuda_relacionada = cleaned_data.get('deuda_relacionada')
        if categoria == 'CUOTAS' and tipo == 'INGRESO' and not deuda_relacionada:
            self.add_error('deuda_relacionada', 'Debe seleccionar una deuda a pagar cuando la categoría es "Cuotas de Socios" y el tipo es "Ingreso"')
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
    socios = forms.CharField(
        widget=forms.HiddenInput(),
        label='IDs de Socios',
        help_text='IDs de socios separados por comas'
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
    
    def clean_socios(self):
        socios_ids = self.cleaned_data['socios']
        if not socios_ids:
            raise forms.ValidationError('Debe seleccionar al menos un socio.')
        
        try:
            # Convertir la cadena de IDs en una lista de enteros
            ids_list = [int(id.strip()) for id in socios_ids.split(',') if id.strip()]
            # Verificar que todos los socios existen
            socios = Socio.objects.filter(id__in=ids_list)
            if len(socios) != len(ids_list):
                raise forms.ValidationError('Algunos socios seleccionados no existen.')
            return socios_ids
        except ValueError:
            raise forms.ValidationError('Formato de IDs de socios inválido.')
    
    def get_socios_queryset(self):
        """Retorna el queryset de socios para el template"""
        return Socio.objects.all() 