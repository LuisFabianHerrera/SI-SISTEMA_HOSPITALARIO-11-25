# gestion_pacientes/models.py
from django.db import models
from django.utils import timezone

class Paciente(models.Model):
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    ci = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    fecha_ingreso = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}"



class Anamnesis(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="anamnesis")
    motivo_consulta = models.TextField()
    signos_vitales = models.TextField()
    historia_enfermedad_actual = models.TextField()
    antecedentes_patologicos = models.TextField()
    antecedentes_no_patologicos = models.TextField()
    antecedentes_gineco_obstetricos = models.TextField(blank=True, null=True)
    antecedentes_familiares = models.TextField()
    fecha_registro = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Anamnesis de {self.paciente}"
    
    
class Diagnostico(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="diagnosticos")
    descripcion = models.TextField()
    especialidad = models.CharField(max_length=100)
    tratamiento = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Diagnóstico de {self.paciente}"

class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name="citas")
    fecha_cita = models.DateTimeField()
    motivo = models.TextField()
    estado_choices = [
        ('P', 'Pendiente'),
        ('C', 'Confirmada'),
        ('R', 'Realizada'),
        ('X', 'Cancelada')
    ]
    estado = models.CharField(max_length=1, choices=estado_choices, default='P')
    fecha_registro = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Cita de {self.paciente} - {self.fecha_cita.strftime('%d/%m/%Y %H:%M')}"
