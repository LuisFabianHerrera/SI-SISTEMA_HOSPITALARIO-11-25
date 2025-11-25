# gestion_administrativa/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta
from .models import Empleado, TurnoEmpleado
from .utils import TURNOS_PREDETERMINADOS
from django.utils import timezone

# Mapeo de días para generar fechas reales
DIAS_SEMANA = {
    'Lunes': 0,
    'Martes': 1,
    'Miércoles': 2,
    'Jueves': 3,
    'Viernes': 4,
    'Sábado': 5,
    'Domingo': 6,
}

@receiver(post_save, sender=Empleado)
def asignar_turnos_automaticos(sender, instance, created, **kwargs):
    """
    Cuando se crea un empleado, le asignamos sus turnos automáticamente
    en base a su cargo y el diccionario TURNOS_PREDETERMINADOS.
    """
    if created and instance.cargo in TURNOS_PREDETERMINADOS:
        config = TURNOS_PREDETERMINADOS[instance.cargo]
        hora_inicio = datetime.strptime(config['horario_inicio'], "%H:%M").time()
        hora_fin = datetime.strptime(config['horario_fin'], "%H:%M").time()

        hoy = timezone.now().date()
        for dia_nombre in config['dias']:
            # Calculamos la fecha próxima para ese día
            weekday_objetivo = DIAS_SEMANA[dia_nombre]
            dias_a_sumar = (weekday_objetivo - hoy.weekday()) % 7
            fecha_turno = hoy + timedelta(days=dias_a_sumar)

            TurnoEmpleado.objects.create(
                empleado=instance,
                fecha=fecha_turno,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin
            )
