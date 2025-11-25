from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Avg # Importamos Avg
from datetime import date 
from django.http import HttpResponse 
from dateutil import parser 
from django_xhtml2pdf.utils import generate_pdf 
from decimal import Decimal

# Importación de los modelos (Asegúrate de que estos nombres sean correctos)
from gestion_pacientes.models import Paciente  # Nuevo modelo Paciente
from .models import (
    GestionAdministrativaEmpleado, 
    GestionAdministrativaCita,
    GestionAdministrativaUsuario
)

# Importaciones locales usadas al final del archivo para los reportes
from gestion_administrativa.models import Empleado, Cita 

# --- Funciones de Soporte y Lógica de Roles (Sin cambios) ---

def es_alto_mando(user):
    """
    Define si el usuario tiene rol de Alto Mando (Staff o Superusuario).
    """
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def is_doctor_by_cargo(empleado):
    """
    Función de Lógica de Negocio: Determina si el empleado es Doctor
    revisando el nombre de su Cargo.
    """
    if empleado and hasattr(empleado, 'cargo') and empleado.cargo:
        cargo_nombre = str(empleado.cargo).lower()
        return 'doctor' in cargo_nombre or 'médico' in cargo_nombre
    return False

# --- 1. Vistas de Redirección y Acceso (Filtrado por Rol) ---

@login_required
def redireccion_principal_view(request):
    """
    Decide dónde enviar al usuario logueado basado en su rol.
    """
    empleado = None
    
    if es_alto_mando(request.user):
        return redirect('dashboard_std') 

    try:
        usuario_ga = GestionAdministrativaUsuario.objects.get(pk=request.user.pk)
        empleado = GestionAdministrativaEmpleado.objects.get(usuario=usuario_ga)

        if is_doctor_by_cargo(empleado):
            return redirect('reportes_doctor') 

        return redirect('dashboard_empleado_general') 

    except (GestionAdministrativaEmpleado.DoesNotExist, GestionAdministrativaUsuario.DoesNotExist):
        pass

    return HttpResponse("Bienvenido. Su rol no tiene un dashboard asignado.", status=200)


# --- 2. Vistas Operacionales (Doctor) ---

@login_required
def reportes_doctor_view(request):
    """
    Vista para Doctores: Reporte de citas (Operacional, solo sus citas).
    """
    empleado = None
    try:
        usuario_ga = GestionAdministrativaUsuario.objects.get(pk=request.user.pk)
        empleado = GestionAdministrativaEmpleado.objects.get(usuario=usuario_ga)

        if not is_doctor_by_cargo(empleado):
             return redirect('std_index') 

        empleado.es_doctor = True
        
    except (GestionAdministrativaEmpleado.DoesNotExist, GestionAdministrativaUsuario.DoesNotExist):
        return redirect('std_index') 
    
    fecha_filtro = request.GET.get('fecha_cita')
    paciente_busqueda = request.GET.get('paciente_busqueda')
    export_pdf = request.GET.get('export') == 'pdf'

    citas_pendientes = GestionAdministrativaCita.objects.filter(
        doctor=empleado,
        estado='Pendiente' 
    )

    if fecha_filtro:
        try:
            fecha_dt = parser.parse(fecha_filtro).date()
            citas_pendientes = citas_pendientes.filter(fecha=fecha_dt)
        except (ValueError, TypeError):
            pass

    if paciente_busqueda:
        citas_pendientes = citas_pendientes.filter(
            Q(paciente__nombre__icontains=paciente_busqueda) | 
            Q(paciente__apellido__icontains=paciente_busqueda)
        )

    citas_pendientes = citas_pendientes.order_by('fecha', 'hora')

    context = {
        'titulo': f'Reporte Operacional de Citas para Dr/a. {empleado.nombre} {empleado.apellido}',
        'empleado': empleado,
        'citas_pendientes': citas_pendientes,
        'citas_pendientes_count': citas_pendientes.count(),
        'fecha_filtro_actual': fecha_filtro,
        'paciente_busqueda_actual': paciente_busqueda,
    }

    if export_pdf:
        return generate_pdf(request, 'std_dashboard/reporte_doctor_pdf.html', context)

    return render(request, 'std_dashboard/reporte_doctor.html', context)
    

@login_required
def gestion_cita_doctor_view(request, cita_id):
    """
    Vista de backend para que el Doctor Acepte o Rechace una cita.
    """
    try:
        usuario_ga = GestionAdministrativaUsuario.objects.get(pk=request.user.pk)
        empleado = GestionAdministrativaEmpleado.objects.get(usuario=usuario_ga)
        
        if not is_doctor_by_cargo(empleado):
            return redirect('std_index') 
            
    except (GestionAdministrativaEmpleado.DoesNotExist, GestionAdministrativaUsuario.DoesNotExist):
        return redirect('std_index') 

    cita = get_object_or_404(GestionAdministrativaCita, pk=cita_id, doctor=empleado)
    accion = request.GET.get('accion')
    
    if accion == 'aceptar':
        cita.estado = 'Aceptada'
    elif accion == 'rechazar':
        cita.estado = 'Rechazada'
    
    cita.save()
    return redirect('reportes_doctor')


# --- 3. Vistas Gerenciales (Alto Mando) (Sin cambios) ---
@login_required
@user_passes_test(es_alto_mando, login_url='/accounts/login/') 
def dashboard_std_view(request):
    """
    Vista principal del Dashboard Gerencial (Alto Mando).
    """
    empleado = None
    
    try:
        usuario_ga = GestionAdministrativaUsuario.objects.get(pk=request.user.pk) 
        empleado = GestionAdministrativaEmpleado.objects.get(usuario=usuario_ga)
        
        if is_doctor_by_cargo(empleado):
            empleado.es_doctor = True 

    except (GestionAdministrativaEmpleado.DoesNotExist, GestionAdministrativaUsuario.DoesNotExist):
        pass

    total_pacientes = Paciente.objects.count()
    
    total_medicos = GestionAdministrativaEmpleado.objects.filter(
        Q(cargo__icontains='doctor') | 
        Q(cargo__icontains='médico')
    ).count()
    
    total_citas_pendientes = GestionAdministrativaCita.objects.filter(estado='Pendiente').count()
    
    total_ingresos = Decimal(55000.75) 
    ingresos_formato = f"${total_ingresos:,.2f}"
    
    datos_ingresos_dashboard = [
        {'mes': 'Ene', 'monto': 12500.00},
        {'mes': 'Feb', 'monto': 18750.50},
        {'mes': 'Mar', 'monto': 25300.25},
        {'mes': 'Abr', 'monto': 21000.00},
    ]

    doctores = GestionAdministrativaEmpleado.objects.filter(
        Q(cargo__icontains='doctor') |
        Q(cargo__icontains='médico')
    )

    datos_desempeno_dashboard = []

    for doctor in doctores:
        total_atendidas = GestionAdministrativaCita.objects.filter(
            doctor=doctor,
            estado='atendida'
        ).count()

        datos_desempeno_dashboard.append({
            'doctor': f"{doctor.nombre}",
            'citas_atendidas': total_atendidas
        })

    context = {
        'titulo': 'Panel Administrativo - Dashboard Gerencial',
        'kpis': [
            {'nombre': 'Pacientes Registrados', 'valor': total_pacientes, 'unidad': 'Personas', 'color': 'bg-success'},
            {'nombre': 'Doctores en Plantilla', 'valor': total_medicos, 'unidad': 'Unidades', 'color': 'bg-info'},
            {'nombre': 'Citas Pendientes (GLOBAL)', 'valor': total_citas_pendientes, 'unidad': 'Citas', 'color': 'bg-warning'},
            {'nombre': 'Ingresos Acumulados', 'valor': ingresos_formato, 'unidad': 'USD', 'color': 'bg-primary'},
        ],
        'empleado': empleado, 
        'datos_ingresos': datos_ingresos_dashboard,
        'datos_desempeno': datos_desempeno_dashboard,
    }
    
    return render(request, 'std_dashboard/dashboard_std.html', context)


@login_required
@user_passes_test(es_alto_mando, login_url='/accounts/login/') 
def reporte_financiero_view(request):
    """
    Vista para Alto Mando: Reporte Financiero (Gerencial - Detallado).
    """
    ingresos_por_mes = [
        {'mes': 'Ene', 'monto': Decimal(12500.00)},
        {'mes': 'Feb', 'monto': Decimal(18750.50)},
        {'mes': 'Mar', 'monto': Decimal(25300.25)},
        {'mes': 'Abr', 'monto': Decimal(21000.00)},
    ]
    total_anual_simulado = sum(item['monto'] for item in ingresos_por_mes)
    context = {
        'titulo': 'Reporte Mensual de Facturación',
        'total_anual': f"${total_anual_simulado:,.2f}",
        'datos_ingresos': ingresos_por_mes
    }
    return render(request, 'std_dashboard/reporte_financiero.html', context)


# --------------------------------------------------------------------------------
# VISTA PRINCIPAL CORREGIDA: reporte_desempeno_view
# --------------------------------------------------------------------------------
@login_required
@user_passes_test(es_alto_mando, login_url='/accounts/login/') 
def reporte_desempeno_view(request):
    """
    Vista para Alto Mando: Reporte de Desempeño Médico, incluyendo promedio de calificación.
    
    NOTA: La lógica de cálculo es correcta. Si el 'promedio_calificacion' es 0, la causa
    más común es que no existen citas con 'estado='atendida'' que además tengan 
    una calificación asignada (campo 'calificacion' con un valor > 0).
    """
    # 1. Obtener todos los médicos
    doctores = Empleado.objects.filter(Q(cargo__icontains='doctor') | Q(cargo__icontains='médico'))

    datos_desempeno = []

    for doctor in doctores:
        # 2. Obtener citas atendidas (CRÍTICO: el valor 'atendida' debe coincidir con la BD)
        citas_atendidas = Cita.objects.filter(doctor=doctor, estado='atendida')
        total_atendidas = citas_atendidas.count()

        # 3. Calcular el promedio de calificación
        # Si no hay calificaciones, .aggregate() devuelve {'prom': None}
        promedio_calificacion_agregado = citas_atendidas.aggregate(prom=Avg('calificacion'))['prom']
        
        # 4. Asignar 0 si es None, o redondear si hay un valor
        if promedio_calificacion_agregado is not None:
            # Si el promedio existe, lo redondeamos a 2 decimales.
            promedio_calificacion_final = round(promedio_calificacion_agregado, 2)
        else:
            # Si es None (no hay citas calificadas), el promedio es 0.
            promedio_calificacion_final = 0 

        datos_desempeno.append({
            'doctor': doctor.nombre,
            'citas_atendidas': total_atendidas,
            'promedio_calificacion': promedio_calificacion_final # Ya es el valor correcto
        })

    total_citas_atendidas = sum(d['citas_atendidas'] for d in datos_desempeno)

    context = {
        'titulo': 'Reporte de Desempeño Médico',
        'total_citas_atendidas': total_citas_atendidas,
        'datos_desempeno': datos_desempeno
    }

    return render(request, 'std_dashboard/reporte_desempeno.html', context)


# --- Vista Redundante (reporte_calificacion_view): Misma Lógica ---
@login_required
@user_passes_test(es_alto_mando, login_url='/accounts/login/')
def reporte_calificacion_view(request):
    # NOTA: Esta vista tiene el mismo objetivo que reporte_desempeno_view. Se recomienda usar solo una.
    doctores = Empleado.objects.filter(Q(cargo__icontains='doctor') | Q(cargo__icontains='médico'))

    datos_desempeno = []

    for doctor in doctores:
        citas_atendidas = Cita.objects.filter(doctor=doctor, estado='atendida')
        total_atendidas = citas_atendidas.count()

        promedio_calificacion_agregado = citas_atendidas.aggregate(prom=Avg('calificacion'))['prom']
        
        if promedio_calificacion_agregado is not None:
            promedio_calificacion_final = round(promedio_calificacion_agregado, 2)
        else:
            promedio_calificacion_final = 0

        datos_desempeno.append({
            'doctor': doctor.nombre,
            'citas_atendidas': total_atendidas,
            'promedio_calificacion': promedio_calificacion_final
        })

    context = {
        'titulo': 'Reporte de Atención de Doctores',
        'total_citas_atendidas': sum(d['citas_atendidas'] for d in datos_desempeno),
        'datos_desempeno': datos_desempeno
    }

    return render(request, 'std_dashboard/reporte_calificacion.html', context)


# --- 4. Vista Operacional para Empleados Generales (Recepcionistas, Admin, etc.) (Sin cambios) ---

@login_required
def dashboard_empleado_general_view(request):
    """
    Vista de dashboard para empleados que no son Alto Mando ni Doctores.
    """
    empleado = None
    try:
        usuario_ga = GestionAdministrativaUsuario.objects.get(pk=request.user.pk)
        empleado = GestionAdministrativaEmpleado.objects.get(usuario=usuario_ga)
    except (GestionAdministrativaEmpleado.DoesNotExist, GestionAdministrativaUsuario.DoesNotExist):
        return redirect('std_index')

    context = {
        'titulo': f'Dashboard Operacional de {empleado.cargo}',
        'empleado': empleado,
        'fecha_actual': date.today().strftime("%d de %B de %Y")
    }
    return render(request, 'std_dashboard/dashboard_empleado_general.html', context)

# --- Vista para que el Paciente califique la Cita (Sin cambios) ---
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

@login_required
def calificar_cita_view(request, cita_id):
    """
    Vista donde un paciente califica su cita (1 a 5) con emojis.
    """
    # Se utiliza el alias 'Cita' importado localmente.
    cita = get_object_or_404(Cita, id=cita_id)

    # Solo permitir calificar si la cita está atendida
    # Es CRÍTICO que el estado coincida: 'atendida'
    if cita.estado != 'atendida':
        messages.error(request, "Solo se pueden calificar citas atendidas.")
        return redirect('home')

    if request.method == 'POST':
        calificacion = request.POST.get('calificacion')
        if calificacion and calificacion.isdigit() and 1 <= int(calificacion) <= 5:
            cita.calificacion = int(calificacion)
            cita.save()
            messages.success(request, "Gracias por calificar al doctor!")
            
            usuario_id = cita.doctor.usuario.id  
            return redirect('pacientes_atendidos', usuario_id=usuario_id)
        else:
            messages.error(request, "Selecciona una calificación válida (1 a 5).")

    emojis = {
        1: '😞',
        2: '😐',
        3: '🙂',
        4: '😃',
        5: '🤩'
    }

    return render(request, 'std_dashboard/calificar_cita.html', {'cita': cita, 'emojis': emojis})