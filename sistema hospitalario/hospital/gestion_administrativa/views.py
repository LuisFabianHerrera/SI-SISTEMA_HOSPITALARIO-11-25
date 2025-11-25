# ==========================================
# IMPORTS
# ==========================================
import datetime
from datetime import date, timedelta
from calendar import monthrange
from collections import defaultdict

from MySQLdb import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required



# Modelos y formularios
from .models import Empleado, Usuario, TurnoEmpleado, HorarioEstandar
from .forms import (
    EmpleadoForm,
    TurnoEmpleadoForm,
    EmpleadoFormEditar,
    AsignarGrupoForm
)
from .utils import calcular_turno_rotado

# ==========================================
# LOGIN / LOGOUT / HOME
# ==========================================
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # Diccionario cargo -> URL de redirección
            redirecciones = {
                'administrador': 'dashboard_std',
                'medico': 'medico_home',
                'enfermero': 'enfermero_home',
                'tecnico': 'tecnico_home',
                'recepcionista': 'recepcionista_home',
                'farmaceutico': 'farmaceutico_home',
                'auxiliar': 'auxiliar_home',
            }

            try:
                empleado = Empleado.objects.get(usuario=user)
                cargo = empleado.cargo.lower()
            except Empleado.DoesNotExist:
                cargo = None

            return redirect(redirecciones.get(cargo, 'home'))

        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'gestion_administrativa/seguridad_login/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def admin_home(request):
    return render(
        request,
        'std_dashboard/dashboard_std.html',
        {'nombre_usuario': request.user.first_name}
    )



@login_required
def empleado_home(request):
    usuario = request.user
    return render(request, 'gestion_administrativa/empleado_home.html', {'usuario': usuario})


@login_required
def medico_home(request):
    usuario = request.user
    try:
        empleado = Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect('home')

    # 🔹 Capturar año y mes desde GET
    year = request.GET.get('year')
    month = request.GET.get('month')

    # Obtener el calendario del empleado
    horario_context = obtener_calendario_empleado(empleado, year=year, month=month)

    # 🔹 Obtener citas en espera del doctor
    citas_en_espera = Cita.objects.filter(
        doctor=empleado,
        estado="en_espera"
    ).order_by("prioridad", "hora")

    # Datos del panel de médico (puedes dejar igual)
    panel_medico = {
        "agenda_consultas": citas_en_espera,
        "pacientes_asignados": [
            {"nombre": "Pedro Gómez", "habitacion": "101A", "estado": "Estable"},
            {"nombre": "Ana Torres", "habitacion": "102B", "estado": "Crítico"},
        ],
        "resultados_pendientes": [
            {"tipo": "Laboratorio", "detalle": "Hemograma pendiente revisión"},
            {"tipo": "Imagen", "detalle": "Radiografía tórax pendiente firma"},
        ],
        "tareas_rapidas": ["Solicitar Interconsulta", "Generar Receta", "Alta Médica"],
        "estadisticas_clave": {
            "ocupacion_camas": "75%",
            "tiempo_promedio_espera": "20 min"
        }
    }

    context = {
        'usuario': usuario,
        'doctor_id': empleado.id,  # 🔹 pasamos el doctor.id para la URL
        **horario_context,
        'panel_medico': panel_medico
    }
    return render(request, 'gestion_administrativa/medico_home.html', context)

@login_required
def enfermero_home(request):
    usuario = request.user
    try:
        empleado = Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect('home')

    # Obtener el calendario del empleado
    horario_context = obtener_calendario_empleado(empleado)

    # Datos del panel de enfermero
    panel_enfermero = {
        "plan_cuidados": [
            {"hora": "08:00", "paciente": "Juan Pérez", "tarea": "Administrar medicación", "realizado": False},
            {"hora": "09:00", "paciente": "María López", "tarea": "Cambio de vendaje", "realizado": True},
        ],
        "departamento": empleado.departamento if empleado.departamento else "Departamento no asignado",
        "alertas_pacientes": [
            {"paciente": "Pedro Gómez", "alerta": "Presión arterial alta"},
            {"paciente": "Ana Torres", "alerta": "Oxígeno bajo"},
        ],
        "gestion_suministros": ["Solicitar Guantes", "Solicitar Jeringas", "Solicitar Suero"],
        "notificaciones": [
            {"de": "Dr. Martínez", "mensaje": "Nueva orden de laboratorio para Juan Pérez"},
            {"de": "Central Enfermería", "mensaje": "Cambio de turno disponible"}
        ]
    }

    # Pasar usuario + horario + panel de enfermero al template
    context = {
        'usuario': usuario,
        **horario_context,
        'panel_enfermero': panel_enfermero
    }
    return render(request, 'gestion_administrativa/enfermero_home.html', context)

@login_required
def tecnico_home(request):
    usuario = request.user
    try:
        empleado = Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect('home')

    # Obtener el calendario del empleado
    horario_context = obtener_calendario_empleado(empleado)

    # Datos del panel de técnico
    panel_tecnico = {
        "ordenes_trabajo": [
            {"hora": "08:00", "paciente": "Juan Pérez", "examen": "Hemograma"},
            {"hora": "09:00", "paciente": "María López", "examen": "Radiografía tórax"},
        ],
        "estado_equipos": [
            {"equipo": "RMN", "estado": "Disponible"},
            {"equipo": "TAC", "estado": "Mantenimiento"},
            {"equipo": "Analizador de Sangre", "estado": "Disponible"}
        ],
        "inventario_reactivos": [
            {"reactivo": "Reactivo A", "stock": 5, "alerta": True},
            {"reactivo": "Reactivo B", "stock": 50, "alerta": False}
        ],
        "tiempos_entrega": {
            "meta": "24h",
            "promedio_actual": "30h"
        }
    }

    # Pasar usuario + horario + panel de técnico al template
    context = {
        'usuario': usuario,
        **horario_context,
        'panel_tecnico': panel_tecnico
    }
    return render(request, 'gestion_administrativa/tecnico_home.html', context)

@login_required
def recepcionista_home(request):
    usuario = request.user
    try:
        empleado = Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect('home')

    # Obtener el calendario del empleado
    horario_context = obtener_calendario_empleado(empleado)

    # Datos del panel de recepcionista
    panel_recepcionista = {
        "sala_espera": [
            {"nombre": "Juan Pérez", "tiempo_espera": "15 min", "medico": "Dr. Martínez"},
            {"nombre": "María López", "tiempo_espera": "5 min", "medico": "Dra. Gómez"},
        ],
        "agenda_dia": [
            {"hora": "08:00", "paciente": "Pedro Gómez", "medico": "Dr. Martínez"},
            {"hora": "08:30", "paciente": "Ana Torres", "medico": "Dra. Gómez"},
            {"hora": "09:00", "paciente": "Luis Rojas", "medico": "Dr. Martínez"},
        ],
        "noticias_alertas": [
            {"mensaje": "Retraso del Dr. Martínez, próxima consulta a las 08:30"},
            {"mensaje": "Sala 3 fuera de servicio temporalmente"}
        ],
        "tareas_rapidas": [
            "Registrar Nuevo Paciente",
            "Asignar Cita",
            "Verificar Cobertura de Seguro"
        ]
    }

    # Pasar usuario + horario + panel de recepcionista al template
    context = {
        'usuario': usuario,
        **horario_context,
        'panel_recepcionista': panel_recepcionista
    }
    return render(request, 'gestion_administrativa/recepcionista_home.html', context)


@login_required
def farmaceutico_home(request):
    usuario = request.user
    try:
        empleado = Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect('home')

    # Obtener el calendario del empleado
    horario_context = obtener_calendario_empleado(empleado)

    # Pasar usuario + horario al template
    context = {
        'usuario': usuario,
        **horario_context
    }
    return render(request, 'gestion_administrativa/farmaceutico_home.html', context)


@login_required
def auxiliar_home(request):
    usuario = request.user
    try:
        empleado = Empleado.objects.get(usuario=usuario)
    except Empleado.DoesNotExist:
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect('home')

    # Obtener el calendario del empleado
    horario_context = obtener_calendario_empleado(empleado)

    # Datos del panel de auxiliar
    panel_auxiliar = {
        "solicitudes_tareas": [
            {"tarea": "Limpieza habitación 101", "estado": "Pendiente"},
            {"tarea": "Traslado paciente sala 3 -> sala 5", "estado": "En progreso"},
        ],
        "checklist_areas": [
            {"area": "Sala 1", "ultimo_accion": "2025-11-18 08:30", "estado": "Requiere limpieza"},
            {"area": "Sala 2", "ultimo_accion": "2025-11-18 09:00", "estado": "Limpia"}
        ],
        "inventario_insumos": [
            {"item": "Toallas", "stock": 50},
            {"item": "Sábanas", "stock": 30},
            {"item": "Desinfectante", "stock": 10, "alerta": True}
        ],
        "rutas_transporte": [
            {"ruta": "Laboratorio -> Sala 3", "estado": "Programada"},
            {"ruta": "Farmacia -> Sala 5", "estado": "Completada"}
        ]
    }

    context = {
        'usuario': usuario,
        **horario_context,
        'panel_auxiliar': panel_auxiliar
    }

    return render(request, 'gestion_administrativa/auxiliar_home.html', context)



@login_required
def home(request):
    if request.user.is_superuser or (
        hasattr(request.user, 'cargo') and request.user.cargo.lower() == 'administrador'
    ):
        return redirect('dashboard_std')
    else:
        return redirect('empleado_home')


# ==========================================
# EMPLEADOS CRUD
# ==========================================
@login_required
def lista_empleados(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver esta página.")
        return redirect('home')

    empleados = Empleado.objects.all().order_by('departamento', 'nombre')

    departamentos = {}
    for empleado in empleados:
        depto = (
            empleado.departamento.nombre
            if hasattr(empleado.departamento, 'nombre')
            else empleado.departamento
        )
        if depto not in departamentos:
            departamentos[depto] = []
        departamentos[depto].append(empleado)

    return render(
        request,
        'gestion_administrativa/empleados/lista_empleados.html',
        {'departamentos': departamentos}
    )


@login_required
def registrar_empleado(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para registrar empleados.")
        return redirect('home')

    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            empleado = form.save(commit=False)
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            usuario = Usuario.objects.create_user(
                username=username,
                password=password,
                cargo=empleado.cargo
            )
            empleado.usuario = usuario
            empleado.save()
            messages.success(request, f"Empleado {empleado.nombre} {empleado.apellido} registrado correctamente.")
            return redirect('lista_empleados')
    else:
        form = EmpleadoForm()

    return render(
        request,
        'gestion_administrativa/empleados/registrar_empleado.html',
        {'form': form}
    )


@login_required
def editar_empleado(request, empleado_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para editar empleados.")
        return redirect('home')

    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == 'POST':
        form = EmpleadoFormEditar(request.POST, instance=empleado)
        if form.is_valid():
            empleado = form.save()
            messages.success(request, f"Empleado {empleado.nombre} {empleado.apellido} actualizado correctamente.")
            return redirect('lista_empleados')
    else:
        form = EmpleadoFormEditar(instance=empleado)

    return render(
        request,
        'gestion_administrativa/empleados/editar_empleado.html',
        {'form': form, 'empleado': empleado}
    )


@login_required
def eliminar_empleado(request, empleado_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para eliminar empleados.")
        return redirect('home')

    empleado = get_object_or_404(Empleado, id=empleado_id)
    usuario = Usuario.objects.filter(cargo=empleado.cargo).first()
    if usuario:
        usuario.delete()
    empleado.delete()

    messages.success(request, "Empleado eliminado correctamente.")
    return redirect('lista_empleados')


# ==========================================
# ASIGNAR GRUPO A EMPLEADO
# ==========================================
@login_required
def asignar_grupo_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == 'POST':
        form = AsignarGrupoForm(request.POST, instance=empleado)
        if form.is_valid():
            empleado = form.save(commit=False)
            empleado.save()

            hoy = datetime.date.today()
            primer_dia_mes = hoy.replace(day=1)
            semana_actual = (hoy.day - 1) // 7

            # Round-robin: calcular día de descanso
            dia_descanso = (empleado.id + semana_actual) % 7

            for i in range(7):
                fecha_turno = primer_dia_mes + datetime.timedelta(days=i + semana_actual * 7)

                # Si es el día de descanso → no crear turno
                if i == dia_descanso:
                    continue  # simplemente saltar este día

                turno = calcular_turno_rotado(empleado.cargo, empleado.grupo_cargo, semana_actual)
                if turno:
                    TurnoEmpleado.objects.update_or_create(
                        empleado=empleado,
                        fecha=fecha_turno,
                        defaults={
                            'hora_inicio': turno['hora_inicio'],
                            'hora_fin': turno['hora_fin']
                        }
                    )

            messages.success(
                request,
                f"Se asignó {empleado.grupo_cargo} a {empleado.nombre}, su horario semanal ha sido generado con rotación y un día de descanso."
            )
            return redirect('lista_turnos')
    else:
        form = AsignarGrupoForm(instance=empleado)

    return render(
        request,
        'gestion_administrativa/empleados/asignar_grupo.html',
        {'form': form, 'empleado': empleado}
    )


# ==========================================
# TURNOS (CRUD + VISTAS)
# ==========================================
@login_required
def lista_turnos(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver los turnos.")
        return redirect('home')

    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    dias_en_mes = monthrange(hoy.year, hoy.month)[1]
    fechas_mes = [primer_dia + timedelta(days=i) for i in range(dias_en_mes)]

    empleados = Empleado.objects.filter(estado='Activo').order_by('departamento', 'nombre')
    departamentos = {}
    for empleado in empleados:
        departamentos.setdefault(empleado.departamento, []).append(empleado)

    turnos = TurnoEmpleado.objects.filter(
        fecha__month=hoy.month, fecha__year=hoy.year
    ).select_related('empleado')

    context = {'departamentos': departamentos, 'fechas_mes': fechas_mes, 'turnos': turnos}
    return render(request, 'gestion_administrativa/turnos/lista_turnos.html', context)


from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import TurnoEmpleadoForm
from .models import Empleado  # importa tu modelo

@login_required
def registrar_turno(request):
    # Solo superusuarios pueden asignar turnos
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para asignar turnos.")
        return redirect('home')

    # Obtener parámetros GET si vienen de la URL
    empleado_id = request.GET.get('empleado')
    fecha = request.GET.get('fecha')

    # Variables para enviar al template
    empleado_obj = None
    departamento_nombre = ''
    grupo_nombre = ''

    if empleado_id:
        try:
            empleado_obj = Empleado.objects.get(id=empleado_id)
            # Si departamento y grupo_cargo son strings en tu modelo, no uses .nombre
            departamento_nombre = empleado_obj.departamento
            grupo_nombre = empleado_obj.grupo_cargo
        except Empleado.DoesNotExist:
            messages.error(request, "Empleado no encontrado.")

    if request.method == 'POST':
        form = TurnoEmpleadoForm(request.POST)
        if form.is_valid():
            turno = form.save()
            messages.success(request, "Turno asignado correctamente.")

            # Redireccionar al calendario del grupo del empleado
            departamento_nombre = turno.empleado.departamento
            grupo_nombre = turno.empleado.grupo_cargo

            return redirect(
                'calendario_turnos_por_grupo',
                departamento=departamento_nombre,
                grupo=grupo_nombre
            )
        else:
            messages.error(request, "La hora de fin no puede ser menor o igual a la hora de inicio.")
    else:
        # Inicializar formulario con valores GET
        initial = {}
        if empleado_id:
            initial['empleado'] = empleado_id
        if fecha:
            initial['fecha'] = fecha
        form = TurnoEmpleadoForm(initial=initial)

    return render(
        request,
        'gestion_administrativa/turnos/registrar_turno.html',
        {
            'form': form,
            'turno': None,  # No hay turno aún
            'empleado': empleado_obj,
            'departamento': departamento_nombre,
            'grupo': grupo_nombre
        }
    )


@login_required
def editar_turno(request, turno_id):
    from .models import TurnoEmpleado  # tu modelo de turno
    try:
        turno = TurnoEmpleado.objects.get(id=turno_id)
    except TurnoEmpleado.DoesNotExist:
        messages.error(request, "Turno no encontrado.")
        return redirect('lista_turnos')

    if request.method == "POST":
        form = TurnoEmpleadoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            messages.success(request, "Turno actualizado correctamente.")
            return redirect(
                'calendario_turnos_por_grupo',
                departamento=turno.empleado.departamento,
                grupo=turno.empleado.grupo_cargo
            )
        else:
            messages.error(request, "Error al actualizar el turno.")
    else:
        form = TurnoEmpleadoForm(instance=turno)

    # Enviar departamento y grupo al template
    departamento = turno.empleado.departamento
    grupo = turno.empleado.grupo_cargo

    return render(request, 'gestion_administrativa/turnos/editar_turno.html', {
        'form': form,
        'turno': turno,
        'departamento': departamento,
        'grupo': grupo
    })


@login_required
def eliminar_turno(request, turno_id):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para eliminar turnos.")
        return redirect('home')

    turno = get_object_or_404(TurnoEmpleado, id=turno_id)

    empleado = turno.empleado   # solo guardamos la relación

    turno.delete()

    messages.success(request, "Turno eliminado correctamente.")

    return redirect(
        'calendario_turnos_por_grupo',
        departamento=empleado.departamento,
        grupo=empleado.grupo_cargo
    )

# ==========================================
# DEPARTAMENTOS Y GRUPOS
# ==========================================
@login_required
def turnos_departamentos(request):
    departamentos = Empleado.objects.values_list('departamento', flat=True).distinct()
    return render(request, 'empleados/lista_turnos.html', {'departamentos': departamentos})


@login_required
def empleados_por_grupo(request, departamento, nombre_grupo):
    empleados = Empleado.objects.filter(departamento=departamento, grupo=nombre_grupo)
    return render(request, 'gestion_administrativa/empleados/tabla_empleados.html', {'empleados': empleados})


@login_required
def vista_departamentos_grupos(request):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver esta sección.")
        return redirect('home')

    departamentos = Empleado.objects.values_list('departamento', flat=True).distinct()
    context = {'departamentos': departamentos, 'grupos': ['Grupo 1', 'Grupo 2', 'Grupo 3']}
    return render(request, 'gestion_administrativa/turnos/departamentos_grupos.html', context)


@login_required
def empleados_por_departamento_y_grupo(request, departamento_nombre, grupo_nombre):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver esta sección.")
        return redirect('home')

    empleados = Empleado.objects.filter(
        departamento=departamento_nombre,
        grupo_cargo=grupo_nombre
    ).order_by('nombre')

    hoy = date.today()
    primer_dia = date(hoy.year, hoy.month, 1)
    dias_en_mes = monthrange(hoy.year, hoy.month)[1]
    fechas_mes = [primer_dia + timedelta(days=i) for i in range(dias_en_mes)]

    turnos_empleados = {}
    for emp in empleados:
        turnos = TurnoEmpleado.objects.filter(empleado=emp, fecha__month=hoy.month, fecha__year=hoy.year)
        turnos_dict = {t.fecha: f"{t.hora_inicio} - {t.hora_fin}" for t in turnos}
        turnos_empleados[emp.id] = turnos_dict

    context = {
        'departamento': departamento_nombre,
        'grupo': grupo_nombre,
        'empleados': empleados,
        'fechas_mes': fechas_mes,
        'turnos_empleados': turnos_empleados
    }

    return render(request, 'gestion_administrativa/turnos/empleados_por_grupo.html', context)


# ==========================================
# CALENDARIOS
# ==========================================
@login_required
def calendario_turnos_mensual(request, year=None, month=None):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver esta sección.")
        return redirect('home')

    hoy = date.today()
    year = int(year) if year else hoy.year
    month = int(month) if month else hoy.month

    primer_dia = date(year, month, 1)
    dias_en_mes = monthrange(year, month)[1]
    fechas_mes = [primer_dia + timedelta(days=i) for i in range(dias_en_mes)]

    semanas = [fechas_mes[i:i+7] for i in range(0, len(fechas_mes), 7)]

    empleados = Empleado.objects.filter(estado='Activo').order_by('departamento', 'grupo_cargo', 'nombre')

    departamentos = {}
    for emp in empleados:
        dep = emp.departamento
        grupo = emp.grupo_cargo or "Sin Grupo"
        departamentos.setdefault(dep, {}).setdefault(grupo, []).append(emp)

    turnos_empleados = {}
    for emp in empleados:
        turnos_empleados[emp.id] = {}
        if not emp.grupo_cargo:
            continue
        semanas_globales = (primer_dia - date(2025, 1, 1)).days // 7
        for idx, fecha in enumerate(fechas_mes):
            semana_mes = idx // 7
            semana_rotacion = semanas_globales + semana_mes
            turno = calcular_turno_rotado(emp.cargo, emp.grupo_cargo, semana_rotacion)
            turnos_empleados[emp.id][fecha] = f"{turno['hora_inicio']} - {turno['hora_fin']}" if turno else "—"

    context = {
        'departamentos': departamentos,
        'semanas': semanas,
        'turnos_empleados': turnos_empleados,
        'month': month,
        'year': year,
    }

    return render(request, 'gestion_administrativa/turnos/calendario_turnos.html', context)


@login_required
def calendario_turnos_por_grupo(request, departamento, grupo):
    if not request.user.is_superuser:
        messages.error(request, "No tienes permiso para ver esta sección.")
        return redirect('home')

    # Obtener mes y año desde GET o usar mes actual
    hoy = date.today()
    year = int(request.GET.get('year', hoy.year))
    month = int(request.GET.get('month', hoy.month))

    # Calcular fechas del mes
    primer_dia = date(year, month, 1)
    dias_en_mes = monthrange(year, month)[1]
    fechas_mes = [primer_dia + timedelta(days=i) for i in range(dias_en_mes)]

    # Marcar el día actual si está en este mes
    dia_actual = hoy if hoy.month == month and hoy.year == year else None

    # Calcular mes anterior y siguiente para navegación
    prev_month = month - 1
    prev_year = year
    if prev_month < 1:
        prev_month = 12
        prev_year -= 1

    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    # Empleados activos del grupo
    empleados = Empleado.objects.filter(
        departamento=departamento,
        grupo_cargo=grupo,
        estado='Activo'
    ).order_by('nombre')

    turnos_empleados = {}

    for emp in empleados:
        turnos_empleados[emp.id] = {}

        # Turnos manuales existentes
        turnos_manual = {
            t.fecha: t for t in TurnoEmpleado.objects.filter(
                empleado=emp,
                fecha__month=month,
                fecha__year=year
            )
        }

        # Semana global basada en fecha de ingreso
        fecha_inicio_rotacion = getattr(emp, 'fecha_ingreso', date(2025, 1, 1))
        semanas_globales = (primer_dia - fecha_inicio_rotacion).days // 7

        for idx, fecha in enumerate(fechas_mes):
            semana_mes = idx // 7
            semana_rotacion = semanas_globales + semana_mes
            dia_semana = idx % 7
            dia_descanso = (emp.id + semana_rotacion) % 7  # round-robin

            # Turnos manuales primero
            if fecha in turnos_manual:
                t = turnos_manual[fecha]
                horario = "Descanso" if not t.hora_inicio and not t.hora_fin else f"{t.hora_inicio} - {t.hora_fin}"
                turnos_empleados[emp.id][fecha] = {"horario": horario, "turno_id": t.id, "manual": True}
            else:
                # Turno automático
                if dia_semana == dia_descanso:
                    horario = "Descanso"
                else:
                    turno = calcular_turno_rotado(emp.cargo, emp.grupo_cargo, semana_rotacion)
                    horario = f"{turno['hora_inicio']} - {turno['hora_fin']}" if turno else "—"

                turnos_empleados[emp.id][fecha] = {"horario": horario, "turno_id": None, "manual": False}

    context = {
        'departamento': departamento,
        'grupo': grupo,
        'empleados': empleados,
        'fechas_mes': fechas_mes,
        'turnos_empleados': turnos_empleados,
        'month': month,
        'year': year,
        'dia_actual': dia_actual,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
    }

    return render(request, 'gestion_administrativa/turnos/calendario_por_grupo.html', context)



#citas y colas




# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Cita
from .forms import CitaForm

# LISTAR
def lista_citas(request):
    citas = Cita.objects.all().order_by('-fecha', '-hora')
    return render(request, 'gestion_administrativa/citas/lista_citas.html', {'citas': citas})


# CREAR
def crear_cita(request):
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_citas')
    else:
        form = CitaForm()
    return render(request, 'gestion_administrativa/citas/registrar_cita.html', {'form': form})


# EDITAR
def editar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if request.method == 'POST':
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            return redirect('lista_citas')
    else:
        form = CitaForm(instance=cita)

    return render(request, 'gestion_administrativa/citas/editar_cita.html', {'form': form})


# ELIMINAR
def eliminar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if request.method == 'POST':
        cita.delete()
        return redirect('lista_citas')
    return render(request, 'gestion_administrativa/citas/eliminar.html', {'cita': cita})


# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Cita
from .utils import generar_numero_atencion

def checkin_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if cita.estado != "pendiente":
        messages.error(request, "La cita ya no puede hacer check-in.")
        return redirect("lista_citas")

    # Obtener departamento del doctor
    departamento = cita.doctor.departamento

    # Generar número de atención
    numero = generar_numero_atencion(departamento)

    # Actualizar
    cita.numero_atencion = numero
    cita.estado = "en_espera"
    cita.save()

    messages.success(request, f"Check-in correcto. Número de atención: {numero}")

    return redirect("cola_espera", doctor_id=cita.doctor.id)


def cola_espera(request, doctor_id):
    citas = Cita.objects.filter(
        doctor_id=doctor_id,
        estado="en_espera"
    ).order_by("prioridad", "hora")

    return render(request, "gestion_administrativa/citas/cola_espera.html", {
        "citas": citas
    })

@login_required
def citas_en_proceso(request, doctor_id):
    # Filtrar solo las citas del doctor que están en progreso
    citas = Cita.objects.filter(
        doctor_id=doctor_id,
        estado="en_progreso"
    ).order_by("hora")  # se puede ordenar por hora de inicio, prioridad, etc.

    return render(request, "gestion_administrativa/citas/citas_en_proceso.html", {
        "citas": citas
    })


@login_required
def atender_siguiente(request, doctor_id):
    # Obtener la cita que está en progreso para este doctor
    cita = Cita.objects.filter(doctor_id=doctor_id, estado="en_progreso").first()

    if not cita:
        messages.info(request, "No hay citas en progreso.")
        return redirect('cola_espera', doctor_id=doctor_id)

    if request.method == "POST":
        cita.hora_fin = timezone.now()
        cita.estado = "atendida"
        cita.save()
        messages.success(request, f"Paciente {cita.paciente} atendido correctamente.")
        return redirect('cola_espera', doctor_id=doctor_id)

    return render(request, "gestion_administrativa/citas/atender_siguiente.html", {
        "cita": cita
    })



# views.py
from django.shortcuts import render, get_object_or_404
from .models import Cita, Empleado
from django.contrib.auth.decorators import login_required

@login_required
def pacientes_atendidos(request, usuario_id):
    # Obtener el empleado correspondiente al usuario
    doctor = get_object_or_404(Empleado, usuario_id=usuario_id, cargo='Medico')
    
    # Obtener las citas atendidas de ese doctor
    citas = Cita.objects.filter(
        doctor=doctor,
        estado='atendida'
    ).order_by('-fecha', 'hora_inicio')
    
    return render(request, 'gestion_administrativa/citas/pacientes_atendidos.html', {
        'doctor': doctor,
        'citas': citas
    })



from collections import defaultdict
from django.contrib.auth.decorators import login_required

@login_required
def colas_de_espera(request):
    # Obtener todas las citas en espera, ordenadas por prioridad y hora
    citas = Cita.objects.filter(
        estado="en_espera"
    ).order_by("prioridad", "hora")

    # Agrupamos por doctor para la plantilla
    colas = defaultdict(list)
    for c in citas:
        colas[c.doctor].append(c)

    return render(request, "gestion_administrativa/citas/colas_de_espera.html", {
        "colas": dict(colas)
    })




from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def comenzar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)

    if cita.estado != "en_espera":
        messages.error(request, "La cita no se puede comenzar.")
        return redirect('cola_espera', doctor_id=cita.doctor.id)

    # Guardar hora de inicio y cambiar estado
    cita.hora_inicio = timezone.now()
    cita.estado = "en_progreso"
    cita.save()

    messages.success(request, f"Cita de {cita.paciente} comenzada correctamente.")
    return redirect('atender_siguiente', doctor_id=cita.doctor.id)


from django.shortcuts import render
from .models import Cita
from django.contrib.auth.decorators import login_required

@login_required
def tablero_en_espera(request):
    # Obtener solo citas en estado "en_espera"
    en_espera = Cita.objects.filter(estado="en_espera").order_by("numero_atencion")
    
    return render(request, "gestion_administrativa/citas/tablero_en_espera.html", {
        "en_espera": en_espera
    })


from datetime import date, timedelta
from calendar import monthrange
from django.contrib import messages
from .models import Empleado, TurnoEmpleado

def obtener_calendario_empleado(empleado, year=None, month=None):
    """Retorna el calendario mensual de turnos para un empleado específico"""

    hoy = date.today()
    year = int(year) if year else hoy.year
    month = int(month) if month else hoy.month

    primer_dia = date(year, month, 1)
    dias_en_mes = monthrange(year, month)[1]
    fechas_mes = [primer_dia + timedelta(days=i) for i in range(dias_en_mes)]

    turnos_mes = {}
    semanas_globales = (primer_dia - date(2025, 1, 1)).days // 7

    for idx, fecha in enumerate(fechas_mes):
        semana_mes = idx // 7
        semana_rotacion = semanas_globales + semana_mes
        dia_semana = idx % 7
        dia_descanso = (empleado.id + semana_rotacion) % 7

        # Turno manual
        try:
            t = TurnoEmpleado.objects.get(empleado=empleado, fecha=fecha)
            if t.hora_inicio is None and t.hora_fin is None:
                horario = "Descanso"
            else:
                horario = f"{t.hora_inicio} - {t.hora_fin}"
            manual = True
        except TurnoEmpleado.DoesNotExist:
            if dia_semana == dia_descanso:
                horario = "Descanso"
            else:
                turno = calcular_turno_rotado(empleado.cargo, empleado.grupo_cargo, semana_rotacion)
                horario = f"{turno['hora_inicio']} - {turno['hora_fin']}" if turno else "—"
            manual = False

        turnos_mes[fecha] = {"horario": horario, "manual": manual}

    # Mes anterior
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    # Mes siguiente
    next_month = month + 1
    next_year = year
    if next_month == 13:
        next_month = 1
        next_year += 1

    return {
        'empleado': empleado,
        'fechas_mes': fechas_mes,
        'turnos_mes': turnos_mes,
        'month': month,
        'year': year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'dia_actual': hoy,
    }





# ---------------------------------------------
# IMPORTS ORDENADOS
# ---------------------------------------------

# Django
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse

# Python estándar
import re

# Modelos externos (otra app)
from gestion_pacientes.models import Paciente

# Modelos locales
from .models import Habitacion, Cama, AsignacionCama, ListaEspera

# Formularios locales
from .forms import HabitacionForm, CamaForm, AsignarCamaForm

# Utilidades locales
from .utils import (
    generar_numero_habitacion,
    TIPOS_POR_DEPARTAMENTO
)

# ---------------------------------------------
#     VISTAS (NO SE MODIFICÓ NADA)
# ---------------------------------------------

#------camas

def registrar_habitacion(request):
    if request.method == 'POST':
        form = HabitacionForm(request.POST)
        if form.is_valid():
            habitacion = form.save(commit=False)
            habitacion.numero = generar_numero_habitacion(habitacion.departamento)
            habitacion.save()
            return redirect('listar_habitaciones')
    else:
        form = HabitacionForm()

    return render(request, 'gestion_administrativa/habitaciones/registrar_habitacion.html', {'form': form})


def listar_habitaciones(request):
    habitaciones = Habitacion.objects.all().order_by('departamento', 'numero')
    return render(request, 'gestion_administrativa/habitaciones/listar_habitaciones.html', {'habitaciones': habitaciones})


def editar_habitacion(request, pk):
    habitacion = get_object_or_404(Habitacion, pk=pk)
    departamento_original = habitacion.departamento

    if request.method == 'POST':
        form = HabitacionForm(request.POST, instance=habitacion)
        
        if form.is_valid():
            habitacion = form.save(commit=False)

            if habitacion.departamento != departamento_original:
                habitacion.numero = generar_numero_habitacion(habitacion.departamento)

            habitacion.save()
            return redirect('listar_habitaciones')

    else:
        form = HabitacionForm(instance=habitacion)

    return render(request, 'gestion_administrativa/habitaciones/editar_habitacion.html', {
        'form': form,
        'habitacion': habitacion,
        'TIPOS_POR_DEPARTAMENTO': TIPOS_POR_DEPARTAMENTO
    })


def eliminar_habitacion(request, habitacion_id):
    try:
        habitacion = Habitacion.objects.get(id=habitacion_id)
        habitacion.delete()
        messages.success(request, "Habitación eliminada correctamente.")
    except Habitacion.DoesNotExist:
        messages.error(request, "La habitación no existe.")

    return redirect('listar_habitaciones')


def listar_camas(request):
    camas = (
        Cama.objects
        .select_related("habitacion")
        .order_by("habitacion__departamento", "habitacion__numero", "codigo")
    )
    return render(
        request,
        "gestion_administrativa/habitaciones/listar_camas.html",
        {"camas": camas}
    )


def registrar_cama(request):
    if request.method == "POST":
        form = CamaForm(request.POST)
        if form.is_valid():
            habitacion = form.cleaned_data['habitacion']

            codigos = habitacion.camas.values_list('codigo', flat=True)

            max_num = 0
            for c in codigos:
                match = re.search(r'-C(\d+)$', c)
                if match:
                    num = int(match.group(1))
                    if num > max_num:
                        max_num = num

            next_num = max_num + 1
            codigo_auto = f"{habitacion.numero}-C{next_num}"

            cama = form.save(commit=False)
            cama.codigo = codigo_auto

            try:
                cama.save()
                messages.success(request, f"✅ Cama registrada con código {codigo_auto}")
                return redirect("listar_camas")
            except IntegrityError:
                messages.error(request, "⚠️ Error: código generado ya existe inesperadamente")
        else:
            messages.error(request, "⚠️ Error en el formulario")
    else:
        form = CamaForm()

    return render(request, "gestion_administrativa/habitaciones/registrar_cama.html", {"form": form})


def editar_cama(request, cama_id):
    cama = get_object_or_404(Cama, id=cama_id)
    habitacion_anterior = cama.habitacion

    if request.method == "POST":
        form = CamaForm(request.POST, instance=cama)
        if form.is_valid():
            cama_editada = form.save(commit=False)
            nueva_habitacion = form.cleaned_data['habitacion']

            if nueva_habitacion != habitacion_anterior:
                total_camas = nueva_habitacion.camas.count() + 1
                cama_editada.codigo = f"{nueva_habitacion.numero}-C{total_camas}"

            cama_editada.save()
            messages.success(request, "✅ Cama actualizada correctamente")
            return redirect("listar_camas")
    else:
        form = CamaForm(instance=cama)

    return render(request, "gestion_administrativa/habitaciones/editar_cama.html", {"form": form})



# habitaciones/views.py

# ==========================================
# IMPORTS
# ==========================================
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from gestion_pacientes.models import Paciente  # <- USO CORRECTO DEL MODELO PACIENTE

from .models import Habitacion, Cama, AsignacionCama, ListaEspera
from .forms import AsignarCamaForm


# ==========================================
# API: Obtener habitaciones por departamento
# ==========================================
def get_habitaciones_por_departamento(request):
    departamento = request.GET.get("departamento")
    habitaciones = Habitacion.objects.filter(
        departamento=departamento,
        estado="disponible"
    )

    data = [
        {
            "id": h.id,
            "numero": h.numero,
            "capacidad": h.capacidad,
            "camas_disponibles": h.camas.filter(estado="disponible").count()
        }
        for h in habitaciones
        if h.camas.filter(estado="disponible").count() > 0
    ]

    return JsonResponse({"habitaciones": data})


# ==========================================
# API: Obtener camas disponibles por habitación
# ==========================================
def get_camas_por_habitacion(request):
    habitacion_id = request.GET.get("habitacion_id")
    camas = Cama.objects.filter(
        habitacion_id=habitacion_id,
        estado="disponible"
    )

    data = [{"id": c.id, "codigo": c.codigo} for c in camas]
    return JsonResponse({"camas": data})


# ==========================================
# Vista: Asignar cama a un paciente
# ==========================================
def asignar_cama(request):
    form = AsignarCamaForm()
    departamento = request.GET.get("departamento", "")
    pacientes_espera = []

    if departamento:
        pacientes_espera = ListaEspera.objects.filter(
            departamento=departamento
        ).order_by("fecha_registro")

    if request.method == "POST":
        ci = request.POST.get("ci")
        cama_id = request.POST.get("cama_id")
        departamento_post = request.POST.get("departamento", "")

        # Buscar paciente
        try:
            paciente = Paciente.objects.get(ci=ci)
        except Paciente.DoesNotExist:
            messages.error(request, "Paciente no encontrado.")
            return redirect(f"{request.path}?departamento={departamento_post}")

        # Buscar cama disponible
        try:
            cama = Cama.objects.get(id=cama_id, estado="disponible")
        except Cama.DoesNotExist:
            messages.error(request, "La cama no está disponible.")
            return redirect(f"{request.path}?departamento={departamento_post}")

        # Asignar cama
        cama.estado = "ocupada"
        cama.save()

        AsignacionCama.objects.create(
            paciente=paciente,
            cama=cama
        )

        # Eliminar de lista de espera
        ListaEspera.objects.filter(
            paciente=paciente,
            departamento=departamento_post
        ).delete()

        messages.success(request, f"Cama {cama.codigo} asignada a {paciente.nombre}.")
        return redirect(f"{request.path}?departamento={departamento_post}")

    return render(request, "gestion_administrativa/habitaciones/asignar_cama.html", {
        "form": form,
        "departamento": departamento,
        "pacientes_espera": pacientes_espera
    })


# ==========================================
# Listar camas asignadas
# ==========================================
def listado_camas_asignadas(request):
    asignaciones = AsignacionCama.objects.select_related(
        'paciente', 'cama', 'cama__habitacion'
    )

    return render(request, "gestion_administrativa/habitaciones/listado_camas_asignadas.html", {
        "asignaciones": asignaciones
    })


# ==========================================
# Liberar cama (pasar a limpieza)
# ==========================================
def liberar_cama(request, asignacion_id):
    asignacion = get_object_or_404(AsignacionCama, id=asignacion_id)
    cama = asignacion.cama

    if cama.estado != "ocupada":
        messages.error(request, "La cama no está ocupada.")
        return redirect("listado_camas_asignadas")

    cama.estado = "limpieza"
    cama.save()

    asignacion.fecha_salida = timezone.now()
    asignacion.save()

    messages.success(request, f"Cama {cama.codigo} ahora está en limpieza.")
    return redirect("listado_camas_asignadas")


# ==========================================
# Confirmar limpieza y volver a disponible
# ==========================================
def confirmar_limpieza(request, cama_id):
    cama = get_object_or_404(Cama, id=cama_id)

    if cama.estado != "limpieza":
        messages.error(request, "La cama no está en proceso de limpieza.")
        return redirect("listar_camas")

    cama.estado = "disponible"
    cama.save()

    messages.success(request, f"Cama {cama.codigo} está disponible.")
    return redirect("listar_camas")


# ==========================================
# Verificar disponibilidad de camas y lista de espera
# ==========================================
def verificar_camas_disponibles(request):
    if request.method == "POST":
        departamento = request.POST.get("departamento")
        ci = request.POST.get("ci")

        # Registrar en lista de espera
        try:
            paciente = Paciente.objects.get(ci=ci)
        except Paciente.DoesNotExist:
            messages.error(request, "Paciente no encontrado.")
            return redirect(f"{reverse('verificar_camas_disponibles')}?departamento={departamento}")

        ListaEspera.objects.create(
            paciente=paciente,
            departamento=departamento
        )

        messages.success(request, f"{paciente.nombre} agregado a la lista de espera de {departamento}.")
        return redirect(f"{reverse('verificar_camas_disponibles')}?departamento={departamento}")

    # GET
    departamento = request.GET.get("departamento")
    camas_disponibles = Cama.objects.filter(
        habitacion__departamento=departamento,
        estado="disponible"
    )

    disponible = camas_disponibles.exists()

    if disponible:
        messages.success(request, f"Hay {camas_disponibles.count()} cama(s) disponible(s) en {departamento}.")
    else:
        messages.warning(request, f"No hay camas disponibles en {departamento}.")

    return render(request, "gestion_administrativa/habitaciones/alerta_camas.html", {
        "departamento": departamento,
        "camas_disponibles": camas_disponibles,
        "disponible": disponible,
        "lista_espera": ListaEspera.objects.filter(departamento=departamento)
    })
