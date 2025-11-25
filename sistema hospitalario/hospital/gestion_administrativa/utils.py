# gestion_administrativa/utils.py

# --------------------------
# Constantes y turnos
# --------------------------
TURNOS_PREDETERMINADOS = {
    'Medico': {
        'horario_inicio': '08:00',
        'horario_fin': '16:00',
        'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    },
    'Enfermero': {
        'horario_inicio': '07:00',
        'horario_fin': '15:00',
        'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
    },
    'Tecnico': {
        'horario_inicio': '09:00',
        'horario_fin': '17:00',
        'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    },
    'Administrador': {
        'horario_inicio': '08:00',
        'horario_fin': '12:00',
        'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    },
    'Recepcionista': {
        'horario_inicio': '08:00',
        'horario_fin': '16:00',
        'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
    },
    'Farmaceutico': {
        'horario_inicio': '10:00',
        'horario_fin': '18:00',
        'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    },
    'Auxiliar': {
        'horario_inicio': '07:00',
        'horario_fin': '13:00',
        'dias': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
    },
}

# --------------------------
# Horarios por grupo
# --------------------------
HORARIOS_POR_GRUPO = {
    'Medico': {
        'Grupo 1': [{'hora_inicio':'08:00','hora_fin':'16:00'},
                    {'hora_inicio':'16:00','hora_fin':'00:00'},
                    {'hora_inicio':'00:00','hora_fin':'08:00'}],
        'Grupo 2': [{'hora_inicio':'16:00','hora_fin':'00:00'},
                    {'hora_inicio':'00:00','hora_fin':'08:00'},
                    {'hora_inicio':'08:00','hora_fin':'16:00'}],
        'Grupo 3': [{'hora_inicio':'00:00','hora_fin':'08:00'},
                    {'hora_inicio':'08:00','hora_fin':'16:00'},
                    {'hora_inicio':'16:00','hora_fin':'00:00'}],
    },
    'Administrador': {
        'Grupo 1': [{'hora_inicio':'08:00','hora_fin':'16:00'}],
        'Grupo 2': [{'hora_inicio':'08:00','hora_fin':'16:00'}],
        'Grupo 3': [{'hora_inicio':'08:00','hora_fin':'16:00'}],
    },
    'Enfermero': {
        'Grupo 1': [{'hora_inicio':'07:00','hora_fin':'15:00'},
                    {'hora_inicio':'15:00','hora_fin':'23:00'},
                    {'hora_inicio':'23:00','hora_fin':'07:00'}],
        'Grupo 2': [{'hora_inicio':'15:00','hora_fin':'23:00'},
                    {'hora_inicio':'23:00','hora_fin':'07:00'},
                    {'hora_inicio':'07:00','hora_fin':'15:00'}],
        'Grupo 3': [{'hora_inicio':'23:00','hora_fin':'07:00'},
                    {'hora_inicio':'07:00','hora_fin':'15:00'},
                    {'hora_inicio':'15:00','hora_fin':'23:00'}],
    },
    'Tecnico': {
        'Grupo 1': [{'hora_inicio':'09:00','hora_fin':'17:00'}],
        'Grupo 2': [{'hora_inicio':'10:00','hora_fin':'18:00'}],
        'Grupo 3': [{'hora_inicio':'11:00','hora_fin':'19:00'}],
    },
    'Recepcionista': {
        'Grupo 1': [{'hora_inicio':'08:00','hora_fin':'16:00'}],
        'Grupo 2': [{'hora_inicio':'09:00','hora_fin':'17:00'}],
        'Grupo 3': [{'hora_inicio':'10:00','hora_fin':'18:00'}],
    },
    'Farmaceutico': {
        'Grupo 1': [{'hora_inicio':'10:00','hora_fin':'18:00'}],
        'Grupo 2': [{'hora_inicio':'11:00','hora_fin':'19:00'}],
        'Grupo 3': [{'hora_inicio':'12:00','hora_fin':'20:00'}],
    },
    'Auxiliar': {
        'Grupo 1': [{'hora_inicio':'07:00','hora_fin':'13:00'}],
        'Grupo 2': [{'hora_inicio':'08:00','hora_fin':'14:00'}],
        'Grupo 3': [{'hora_inicio':'09:00','hora_fin':'15:00'}],
    },
}


# --------------------------
# Función para calcular turno rotado
# --------------------------
def calcular_turno_rotado(cargo, grupo, semana_index):
    """
    Retorna el turno correspondiente según la semana y grupo.
    semana_index: número de semana desde un punto fijo
    """
    try:
        turnos = HORARIOS_POR_GRUPO[cargo][grupo]
        index = semana_index % len(turnos)
        return turnos[index]
    except KeyError:
        return None

# --------------------------
# Generar número de atención (importación local para evitar ciclo)
# --------------------------
def generar_numero_atencion(departamento_nombre):
    """
    Genera un numero como: CARD-001
    """
    cod = departamento_nombre[:4].upper()
    from .models import Cita  # importación local

    existentes = Cita.objects.filter(numero_atencion__startswith=cod).count()
    consecutivo = existentes + 1

    return f"{cod}-{consecutivo:03d}"

# --------------------------
# Lista de departamentos
# --------------------------
DEPARTAMENTOS = [
    ('Emergencias', 'Emergencias'),
    ('Hospitalización', 'Hospitalización'),
    ('Consulta Externa', 'Consulta Externa'),
    ('Pediatría', 'Pediatría'),
    ('Ginecología', 'Ginecología'),
    ('Laboratorio', 'Laboratorio'),
    ('Farmacia', 'Farmacia'),
    ('Administración', 'Administración'),
    ('Quirófano', 'Quirófano'),
    ('Radiología', 'Radiología'),
    ('Cardiología', 'Cardiología'),
    ('UCI', 'UCI (Unidad de Cuidados Intensivos)'),
]

# --------------------------
# Tipos de habitación por departamento
# --------------------------
TIPOS_POR_DEPARTAMENTO = {
    'Emergencias': ['Camas de observación', 'Cubículos individuales', 'Cubículos compartidos', 'Sala de trauma', 'Área de choque'],
    'Hospitalización': ['Individual', 'Doble', 'Múltiple', 'Aislamiento'],
    'Consulta Externa': ['Cubículo de consulta', 'Sala de procedimientos menores'],
    'Pediatría': ['Individual', 'Compartida', 'Cama acompañante', 'Aislamiento pediátrico'],
    'Ginecología': ['Preparto', 'Postparto', 'Individual', 'Doble', 'Suite VIP'],
    'Laboratorio': [],
    'Farmacia': [],
    'Administración': [],
    'Quirófano': ['Quirófano', 'Área de recuperación'],
    'Radiología': ['Sala de examen', 'Área de espera'],
    'Cardiología': ['Individual', 'Doble', 'UCI cardíaca'],
    'UCI': ['Individual con soporte vital', 'Aislamiento'],
}

# --------------------------
# Función para obtener horario de empleado (importación local)
# --------------------------
def obtener_horario_empleado(empleado):
    """
    Devuelve el horario de un empleado según su cargo y grupo.
    La importación de modelos se hace local para evitar importación circular.
    """
    from .models import Empleado  # importación local si se requiere usar métodos o consultas
    # Puedes usar TURNOS_PREDETERMINADOS o HORARIOS_POR_GRUPO aquí
    cargo = empleado.cargo
    grupo = getattr(empleado, 'grupo_cargo', None)
    
    if grupo is None:
        return TURNOS_PREDETERMINADOS.get(cargo)
    
    # Si tiene grupo, buscar en HORARIOS_POR_GRUPO
    turnos = HORARIOS_POR_GRUPO.get(cargo, {}).get(grupo)
    if turnos:
        return turnos[0]  # por simplicidad, devuelve el primer turno
    return TURNOS_PREDETERMINADOS.get(cargo)



def generar_numero_habitacion(departamento):
    from .models import Habitacion

    # Obtener las habitaciones del depto
    habitaciones = Habitacion.objects.filter(departamento=departamento)

    if not habitaciones.exists():
        return f"{departamento[:3].upper()}001"

    # Obtener el valor máximo
    max_num = 0
    for h in habitaciones:
        try:
            sec = int(h.numero[3:])
            max_num = max(max_num, sec)
        except:
            pass

    nuevo_numero = max_num + 1
    return f"{departamento[:3].upper()}{nuevo_numero:03d}"
