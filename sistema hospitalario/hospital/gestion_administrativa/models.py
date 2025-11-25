# ============================
# IMPORTS
# ============================

from datetime import date, time, timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils import timezone

# Importaciones locales
from .utils import DEPARTAMENTOS
from gestion_pacientes.models import Paciente


# ============================
# 1️⃣ ROLES
# ============================

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Ej: 'Administrador', 'Médico', 'Técnico'
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# ============================
# 2️⃣ EMPLEADOS
# ============================

class Empleado(models.Model):
    ESTADOS = [
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
        ('Vacaciones', 'Vacaciones'),
    ]

    CARGOS = [
        ('Medico', 'Médico'),
        ('Enfermero', 'Enfermero'),
        ('Tecnico', 'Técnico'),
        ('Administrador', 'Administrador'),
        ('Recepcionista', 'Recepcionista'),
        ('Farmaceutico', 'Farmacéutico'),
        ('Auxiliar', 'Auxiliar'),
    ]

    GRUPOS = [
        ('Grupo 1', 'Grupo 1'),
        ('Grupo 2', 'Grupo 2'),
        ('Grupo 3', 'Grupo 3'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=50, default='')
    cargo = models.CharField(max_length=50, choices=CARGOS)
    departamento = models.CharField(max_length=50, choices=DEPARTAMENTOS, null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Activo')
    usuario = models.OneToOneField('gestion_administrativa.Usuario', on_delete=models.CASCADE, null=True, blank=True)
    grupo_cargo = models.CharField(max_length=10, choices=GRUPOS, blank=True, null=True)
    horario = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.cargo}"


# ============================
# 3️⃣ TURNOS / HORARIOS DE EMPLEADOS
# ============================

class TurnoEmpleado(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='turnos')
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.empleado.nombre} ({self.fecha} {self.hora_inicio}-{self.hora_fin})"


# ============================
# 4️⃣ USUARIOS (SEGURIDAD Y ACCESO)
# ============================

class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("El usuario debe tener un nombre de usuario")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class Usuario(AbstractUser):
    cargo = models.CharField(max_length=50, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='usuarios',
        blank=True,
        help_text='Grupos a los que pertenece el usuario.',
        verbose_name='grupos',
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usuarios_permisos',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        verbose_name='permisos de usuario',
    )

    def __str__(self):
        return f"{self.username} ({self.cargo})"


# ============================
# 5️⃣ MANTENIMIENTO HOSPITALARIO
# ============================

class Mantenimiento(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Realizado', 'Realizado'),
    ]

    area = models.CharField(max_length=50)
    fecha = models.DateField()
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    tecnico_responsable = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mantenimientos'
    )

    def __str__(self):
        return f"{self.area} - {self.estado} ({self.fecha})"


class HorarioEstandar(models.Model):
    cargo = models.CharField(max_length=50, unique=True)
    hora_inicio = models.TimeField(default=time(8, 0))
    hora_fin = models.TimeField(default=time(16, 0))

    def __str__(self):
        return f"{self.cargo}: {self.hora_inicio} - {self.hora_fin}"


# ============================
# 6️⃣ CITAS Y COLAS
# ============================

class Cita(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_espera', 'En espera'),
        ('atendida', 'Atendida'),
        ('cancelada', 'Cancelada'),
        ('en_progreso', 'En Progreso'),
    ]

    paciente = models.CharField(max_length=100)
    doctor = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        limit_choices_to={'cargo': 'Medico'}
    )
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    numero_atencion = models.CharField(max_length=20, null=True, blank=True)
    prioridad = models.IntegerField(default=1)
    hora_inicio = models.DateTimeField(null=True, blank=True)
    hora_fin = models.DateTimeField(null=True, blank=True)
    calificacion = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.paciente} - {self.doctor}"


# ============================
# 7️⃣ HABITACIONES Y CAMAS
# ============================

class Habitacion(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    departamento = models.CharField(max_length=50, choices=DEPARTAMENTOS)
    tipo = models.CharField(max_length=50)
    capacidad = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=20,
        choices=[('disponible','Disponible'),('mantenimiento','En mantenimiento')],
        default='disponible'
    )

    def __str__(self):
        return f'Habitación {self.numero} ({self.tipo} - {self.departamento})'


class Cama(models.Model):
    ESTADOS = [
        ("disponible", "Disponible"),
        ("ocupada", "Ocupada"),
        ("limpieza", "En limpieza"),
        ("bloqueada", "Bloqueada / No usable"),
    ]

    codigo = models.CharField(max_length=10, unique=True)
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name="camas"
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default="disponible")

    def __str__(self):
        return f"Cama {self.codigo} - Hab. {self.habitacion.numero}"


from gestion_pacientes.models import Paciente  # Importa el nuevo modelo

class AsignacionCama(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)  # Apunta al nuevo Paciente
    cama = models.ForeignKey(Cama, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    fecha_salida = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.paciente} → {self.cama}"


class ListaEspera(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)  # Apunta al nuevo Paciente
    departamento = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.paciente.nombre} - {self.departamento}"


# ============================
# 8️⃣ MEDICAMENTOS
# ============================

class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    controlado = models.BooleanField(default=False)

    def movimientos_recientes(self):
        return self.movimientos_set.filter(fecha__gte=date.today() - timedelta(days=7)).count()
