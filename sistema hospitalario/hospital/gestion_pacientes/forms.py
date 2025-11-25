# gestion_pacientes/forms.py
from django import forms
from .models import Paciente
from .models import Anamnesis
from .models import Diagnostico
from .models import Cita

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = [
            'nombre', 'apellido_paterno', 'apellido_materno',
            'ci', 'fecha_nacimiento', 'genero', 'telefono',
            'direccion'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class AnamnesisForm(forms.ModelForm):
    class Meta:
        model = Anamnesis
        fields = [
            'motivo_consulta',
            'signos_vitales',
            'historia_enfermedad_actual',
            'antecedentes_patologicos',
            'antecedentes_no_patologicos',
            'antecedentes_gineco_obstetricos',
            'antecedentes_familiares',
        ]
        widgets = {
            'motivo_consulta': forms.Textarea(attrs={'rows':2}),
            'signos_vitales': forms.Textarea(attrs={'rows':2}),
            'historia_enfermedad_actual': forms.Textarea(attrs={'rows':2}),
            'antecedentes_patologicos': forms.Textarea(attrs={'rows':2}),
            'antecedentes_no_patologicos': forms.Textarea(attrs={'rows':2}),
            'antecedentes_gineco_obstetricos': forms.Textarea(attrs={'rows':2}),
            'antecedentes_familiares': forms.Textarea(attrs={'rows':2}),
        }

    def __init__(self, *args, **kwargs):
        paciente_genero = kwargs.pop('paciente_genero', None)
        super().__init__(*args, **kwargs)
        if paciente_genero == 'M':
            self.fields['antecedentes_gineco_obstetricos'].widget.attrs['readonly'] = True
            self.fields['antecedentes_gineco_obstetricos'].required = False
            
class DiagnosticoForm(forms.ModelForm):
    class Meta:
        model = Diagnostico
        fields = ['descripcion', 'especialidad', 'tratamiento', 'fecha_inicio', 'fecha_fin']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows':2}),
            'tratamiento': forms.Textarea(attrs={'rows':2}),
            'fecha_inicio': forms.DateInput(attrs={'type':'date'}),
            'fecha_fin': forms.DateInput(attrs={'type':'date'}),
        }
class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['fecha_cita', 'motivo', 'estado']
        widgets = {
            'fecha_cita': forms.DateTimeInput(attrs={'type':'datetime-local'}),
            'motivo': forms.Textarea(attrs={'rows':2}),
        }
