from django.db import models

# --- Modelos del Core de Django y Tablas Auxiliares (Sin cambios) ---

class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('GestionAdministrativaUsuario', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


# --- Modelos de Gestión Administrativa (Donde se realizaron los cambios) ---

class GestionAdministrativaAsignacioncama(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha_ingreso = models.DateTimeField()
    cama = models.ForeignKey('GestionAdministrativaCama', models.DO_NOTHING)
    paciente = models.ForeignKey('GestionAdministrativaPaciente', models.DO_NOTHING)
    fecha_salida = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_asignacioncama'


class GestionAdministrativaCama(models.Model):
    id = models.BigAutoField(primary_key=True)
    codigo = models.CharField(unique=True, max_length=10)
    estado = models.CharField(max_length=20)
    habitacion = models.ForeignKey('GestionAdministrativaHabitacion', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_cama'


class GestionAdministrativaCita(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20)
    doctor = models.ForeignKey('GestionAdministrativaEmpleado', models.DO_NOTHING)
    # CRÍTICO: El campo paciente debe ser una FK, pero si es un CharField, se mantiene:
    paciente = models.CharField(max_length=100) 
    numero_atencion = models.CharField(max_length=20, blank=True, null=True)
    prioridad = models.IntegerField()
    hora_fin = models.DateTimeField(blank=True, null=True)
    hora_inicio = models.DateTimeField(blank=True, null=True)
    
    # ----------------------------------------------------
    # FIX PRINCIPAL: Campo de Calificación Faltante
    # ----------------------------------------------------
    calificacion = models.IntegerField(
        blank=True, 
        null=True, 
        help_text="Calificación de la cita (1-5)."
    ) 

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_cita'


class GestionAdministrativaEmpleado(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    # Se añade 'apellido' ya que se usa en views.py (aunque no estaba en la versión anterior, es común)
    apellido = models.CharField(max_length=100, default='') 
    cargo = models.CharField(max_length=50)
    departamento = models.CharField(max_length=50, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    estado = models.CharField(max_length=20)
    usuario = models.OneToOneField('GestionAdministrativaUsuario', models.DO_NOTHING, blank=True, null=True)
    grupo_cargo = models.CharField(max_length=10, blank=True, null=True)
    horario = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_empleado'


class GestionAdministrativaHabitacion(models.Model):
    id = models.BigAutoField(primary_key=True)
    numero = models.CharField(unique=True, max_length=10)
    departamento = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    capacidad = models.PositiveIntegerField()
    estado = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_habitacion'


class GestionAdministrativaHorarioestandar(models.Model):
    id = models.BigAutoField(primary_key=True)
    cargo = models.CharField(unique=True, max_length=50)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_horarioestandar'


class GestionAdministrativaListaespera(models.Model):
    id = models.BigAutoField(primary_key=True)
    departamento = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField()
    paciente = models.ForeignKey('GestionAdministrativaPaciente', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_listaespera'


class GestionAdministrativaMantenimiento(models.Model):
    id = models.BigAutoField(primary_key=True)
    area = models.CharField(max_length=50)
    fecha = models.DateField()
    descripcion = models.TextField()
    estado = models.CharField(max_length=20)
    tecnico_responsable = models.ForeignKey(GestionAdministrativaEmpleado, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_mantenimiento'


class GestionAdministrativaPaciente(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    ci = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_paciente'


class GestionAdministrativaRol(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_rol'


class GestionAdministrativaTurnoempleado(models.Model):
    id = models.BigAutoField(primary_key=True)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    empleado = models.ForeignKey(GestionAdministrativaEmpleado, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_turnoempleado'


class GestionAdministrativaUsuario(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    cargo = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_usuario'


class GestionAdministrativaUsuarioGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(GestionAdministrativaUsuario, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_usuario_groups'
        unique_together = (('usuario', 'group'),)


class GestionAdministrativaUsuarioUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(GestionAdministrativaUsuario, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'gestion_administrativa_usuario_user_permissions'
        unique_together = (('usuario', 'permission'),)