# ---------------------------------------------
# IMPORTS ORDENADOS
# ---------------------------------------------

# Django
from django import forms
from django.core.exceptions import ValidationError

# Modelos de la misma app
from .models import (
    Empleado,
    Usuario,
    TurnoEmpleado,
    Habitacion,
    Cama,
    DEPARTAMENTOS
)

# Modelos de otras apps
from gestion_administrativa.models import Empleado  # Para citas
from gestion_pacientes.models import Paciente
from .models import Cita  # <-- Si Cita está en la misma app

# Utilidades locales
from .utils import generar_numero_habitacion

# ---------------------------------------------
# FORMULARIOS
# ---------------------------------------------

# ------------------------------
# Empleados y turnos
# ------------------------------

class EmpleadoForm(forms.ModelForm):
    # Campos para crear también el usuario
    username = forms.CharField(max_length=150, required=True, help_text="Nombre de usuario para login")
    password = forms.CharField(widget=forms.PasswordInput, required=True, help_text="Contraseña inicial")

    class Meta:
        model = Empleado
        fields = ['nombre','apellido', 'cargo', 'departamento', 'telefono', 'estado', 'username', 'password']


class EmpleadoFormEditar(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['nombre', 'apellido', 'cargo', 'departamento', 'telefono', 'estado']


class TurnoEmpleadoForm(forms.ModelForm):
    class Meta:
        model = TurnoEmpleado
        fields = ['empleado', 'fecha', 'hora_inicio', 'hora_fin']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")

        if hora_inicio and hora_fin and hora_fin <= hora_inicio:
            raise ValidationError("La hora de fin debe ser mayor que la hora de inicio.")

        return cleaned_data


class AsignarGrupoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['grupo_cargo']
        widgets = {
            'grupo_cargo': forms.Select(attrs={'class': 'form-select'})
        }


# ------------------------------
# Citas
# ------------------------------

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['paciente', 'doctor', 'fecha', 'hora', 'estado']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'hora': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}, format='%H:%M'),
            'paciente': forms.TextInput(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['fecha'].initial = self.instance.fecha
            self.fields['hora'].initial = self.instance.hora


# ------------------------------
# Habitaciones
# ------------------------------

class HabitacionForm(forms.ModelForm):
    class Meta:
        model = Habitacion
        fields = ['departamento', 'tipo', 'capacidad', 'estado']
        widgets = {
            'departamento': forms.Select(attrs={'id': 'departamento', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'id': 'tipo', 'class': 'form-control'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }


class CamaForm(forms.ModelForm):
    class Meta:
        model = Cama
        fields = ["habitacion", "estado"]
        widgets = {
            "habitacion": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        habitacion = cleaned_data.get("habitacion")

        if habitacion:
            total_camas = habitacion.camas.count()
            if total_camas >= habitacion.capacidad:
                raise forms.ValidationError(
                    f"⚠️ La habitación {habitacion.numero} ya tiene el máximo ({habitacion.capacidad}) de camas."
                )
        return cleaned_data


# ------------------------------
# Asignación de camas
# ------------------------------

class AsignarCamaForm(forms.Form):
    ci = forms.CharField(label="CI del paciente")
    departamento = forms.ChoiceField(label="Departamento", choices=DEPARTAMENTOS, required=False)
    habitacion_id = forms.ChoiceField(label="Habitación", choices=[], required=False)
    cama_id = forms.ChoiceField(label="Cama", choices=[], required=False)
