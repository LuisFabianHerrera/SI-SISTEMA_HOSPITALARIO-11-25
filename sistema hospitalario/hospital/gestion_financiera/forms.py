# facturacion/forms.py

from django import forms
from django.core.exceptions import ValidationError

# Modelos locales
from .models import (
    Factura,
    DetalleFactura,
    ServicioFacturable,
    Aseguradora,
    PlanSeguro,
    Reclamacion,
    Transaccion,
    MetodoPago
)

# Modelos de otras apps
from gestion_administrativa.models import Paciente

# ==========================================
# FORMULARIOS DE FACTURACIÓN
# ==========================================

class FacturaForm(forms.ModelForm):
    class Meta:
        model = Factura
        fields = ['paciente', 'estado', 'notas', 'transaccion_pago']

class DetalleFacturaForm(forms.ModelForm):
    class Meta:
        model = DetalleFactura
        fields = ['servicio', 'cantidad', 'precio_unitario_facturado']

class ServicioFacturableForm(forms.ModelForm):
    class Meta:
        model = ServicioFacturable
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ==========================================
# ASEGURADORAS Y PLANES DE SEGURO
# ==========================================

class AseguradoraForm(forms.ModelForm):
    class Meta:
        model = Aseguradora
        fields = ['nombre', 'contacto_email', 'contacto_telefono']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej: Seguros Vida Plena', 'class': 'form-control'}),
            'contacto_email': forms.EmailInput(attrs={'placeholder': 'contacto@ejemplo.com', 'class': 'form-control'}),
            'contacto_telefono': forms.TextInput(attrs={'placeholder': 'Ej: 1234-5678', 'class': 'form-control'}),
        }

class PlanSeguroForm(forms.ModelForm):
    class Meta:
        model = PlanSeguro
        fields = ['nombre_plan', 'cobertura_porcentaje', 'deducible']
        labels = {
            'cobertura_porcentaje': 'Cobertura (%)',
            'nombre_plan': 'Nombre del Plan',
        }
        widgets = {
            'nombre_plan': forms.TextInput(attrs={'placeholder': 'Ej: Plan Básico / Plan Familiar', 'class': 'form-control'}),
            'cobertura_porcentaje': forms.NumberInput(attrs={'placeholder': 'Ej: 80.00', 'step': '0.01', 'min': '0', 'class': 'form-control'}),
            'deducible': forms.NumberInput(attrs={'placeholder': 'Ej: 100.00', 'step': '0.01', 'min': '0', 'class': 'form-control'}),
        }

class ReclamacionForm(forms.ModelForm):
    class Meta:
        model = Reclamacion
        fields = ['paciente', 'plan_seguro', 'fecha_servicio', 'monto_reclamado']
        widgets = {
            'fecha_servicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'monto_reclamado': forms.NumberInput(attrs={'placeholder': 'Monto total de la factura', 'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'plan_seguro': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # PlanSeguro ordenado por aseguradora y nombre de plan
        self.fields['plan_seguro'].queryset = PlanSeguro.objects.select_related('aseguradora').order_by('aseguradora__nombre', 'nombre_plan')
        self.fields['plan_seguro'].label_from_instance = lambda obj: f"{obj.aseguradora.nombre} - {obj.nombre_plan}"

        # Paciente ordenado correctamente según tu modelo
        self.fields['paciente'].queryset = Paciente.objects.all().order_by('apellido_paterno', 'apellido_materno', 'nombre')


# ==========================================
# FORMULARIO DE TRANSACCIONES
# ==========================================

class TransaccionForm(forms.ModelForm):
    """Formulario basado en el modelo Transaccion."""

    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all().order_by('apellido_paterno', 'apellido_materno', 'nombre'),
        label="Paciente"
    )
    metodo_pago = forms.ModelChoiceField(
        queryset=MetodoPago.objects.all().order_by('nombre'),
        label="Método de Pago"
    )

    class Meta:
        model = Transaccion
        fields = ['paciente', 'monto', 'tipo', 'metodo_pago', 'descripcion', 'referencia', 'estado']
        widgets = {
            'monto': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01', 'class': 'form-control'}),
            'tipo': forms.Select(choices=Transaccion.TIPOS, attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'referencia': forms.TextInput(attrs={'placeholder': 'Número de referencia bancaria o N/A', 'class': 'form-control'}),
            'estado': forms.Select(choices=Transaccion.ESTADOS, attrs={'class': 'form-control'}),
        }
        labels = {
            'paciente': 'Paciente',
            'monto': 'Monto ($)',
            'tipo': 'Tipo de Transacción',
            'metodo_pago': 'Método de Pago',
            'descripcion': 'Descripción',
            'referencia': 'Referencia',
            'estado': 'Estado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Añadir clase bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
