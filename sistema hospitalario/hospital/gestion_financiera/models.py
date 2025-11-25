# facturacion/models.py
from django.db import models
from gestion_pacientes.models import Paciente  # Nuevo modelo Paciente
from django.utils import timezone


# ============================
# 1️⃣ SERVICIO FACTURABLE
# ============================
class ServicioFacturable(models.Model):
    """Representa un ítem o servicio que puede ser facturado."""
    nombre = models.CharField(max_length=100)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio_unitario})"

    class Meta:
        verbose_name_plural = "Servicios Facturables"


# ============================
# 2️⃣ FACTURA
# ============================
class Factura(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Pagada', 'Pagada'),
        ('Anulada', 'Anulada'),
    ]

    paciente = models.ForeignKey(
        Paciente,  # Apunta al nuevo modelo
        on_delete=models.PROTECT,
        related_name='facturas'
    )
    fecha_emision = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaccion_pago = models.OneToOneField(
        'Transaccion',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='factura'
    )
    notas = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Factura #{self.pk} - {self.paciente.nombre}"

    class Meta:
        ordering = ['-fecha_emision']


# ============================
# 3️⃣ DETALLE DE FACTURA
# ============================
class DetalleFactura(models.Model):
    """Representa cada línea de ítems dentro de una Factura."""
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    servicio = models.ForeignKey(
        ServicioFacturable,
        on_delete=models.PROTECT
    )
    cantidad = models.IntegerField(default=1)
    precio_unitario_facturado = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.servicio.nombre} en Factura #{self.factura.pk}"

    class Meta:
        verbose_name_plural = "Detalles de Factura"


# ============================
# aseguradoras y reclamaciones
# ============================


class Aseguradora(models.Model):
    """Registro de las compañías de seguros que trabajan con el hospital."""
    nombre = models.CharField(max_length=100, unique=True)
    contacto_email = models.EmailField(blank=True, null=True)
    contacto_telefono = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        verbose_name = "Aseguradora"
        verbose_name_plural = "Aseguradoras"
    
    def __str__(self):
        return self.nombre


class PlanSeguro(models.Model):
    """Detalles de los planes ofrecidos por cada aseguradora."""
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.CASCADE, related_name='planes')
    nombre_plan = models.CharField(max_length=100)
    cobertura_porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Porcentaje de cobertura (Ej: 80.00)",
        verbose_name="% Cobertura"
    )
    deducible = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Plan de Seguro"
        verbose_name_plural = "Planes de Seguro"
        unique_together = ('aseguradora', 'nombre_plan') 

    def __str__(self):
        return f"{self.aseguradora.nombre} - {self.nombre_plan}"


class Reclamacion(models.Model):
    """Solicitud de pago a la aseguradora por servicios prestados al paciente."""
    ESTADOS = [
        ('ENVIADA', 'Enviada'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADA', 'Aprobada'),
        ('DENEGADA', 'Denegada'),
        ('PAGADA', 'Pagada por Aseguradora'),
    ]

    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT, related_name='reclamaciones')  # Nuevo FK
    plan_seguro = models.ForeignKey(PlanSeguro, on_delete=models.PROTECT)
    fecha_servicio = models.DateField(verbose_name='Fecha de Servicio')
    monto_reclamado = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Monto Reclamado')
    monto_aprobado = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Monto Aprobado'
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='ENVIADA')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación del Registro')

    class Meta:
        verbose_name = "Reclamación"
        verbose_name_plural = "Reclamaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Reclamación #{self.id} de {self.paciente.get_full_name()}"


# transacciones/models.py
from django.db import models
from django.utils import timezone
from gestion_pacientes.models import Paciente  # Nuevo modelo

# ============================
# 1️⃣ MÉTODOS DE PAGO
# ============================
class MetodoPago(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# ============================
# 2️⃣ TRANSACCIONES
# ============================
class Transaccion(models.Model):
    TIPOS = [
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso'),
        ('Reembolso', 'Reembolso'),
    ]

    ESTADOS = [
        ('Completada', 'Completada'),
        ('Pendiente', 'Pendiente'),
        ('Fallida', 'Fallida'),
        ('Cancelada', 'Cancelada'),
    ]

    paciente = models.ForeignKey(
        Paciente, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transacciones'
    )
    cita = models.CharField(max_length=100, null=True, blank=True)
    fecha_transaccion = models.DateTimeField(default=timezone.now)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.PROTECT)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='Completada')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} de ${self.monto} - {self.paciente.nombre if self.paciente else 'N/A'}"

    class Meta:
        ordering = ['-fecha_transaccion']
